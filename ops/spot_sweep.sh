#!/usr/bin/env bash
# Launch a preemption-tolerant spot worker for a sharded certificate sweep.
#
#   ./spot_sweep.sh launch  <job> <shard-lo> <shard-hi> [cores]
#   ./spot_sweep.sh status  <job>
#   ./spot_sweep.sh collect <job>
#   ./spot_sweep.sh stop    <job>      # STOP the VM (keeps disk, ~$0.10/GB/mo)
#   ./spot_sweep.sh destroy <job>      # DELETE the VM and its disk
#
# Design notes, and why each choice:
#
#  * SPOT, with --instance-termination-action=STOP. Spot is 60-70% off and
#    this workload tolerates interruption; STOP (not DELETE) means a
#    preemption leaves the disk and its checkpoints intact, and `launch`
#    on an existing stopped VM simply restarts it where it left off.
#  * n2-highcpu. E2_CPUS quota in this project is 24; N2_CPUS is 200. The
#    work is CPU-bound with a small per-unit working set, so highcpu
#    (1 GB/vCPU) is the right shape and the cheapest per core.
#  * Results go to a GCS bucket, not the boot disk, so a preemption during
#    the final minute cannot lose the run, and `collect` works whether or
#    not the VM still exists.
#  * MAX_HOURS is a hard self-destruct. A forgotten VM is the single most
#    common way this kind of work quietly costs real money.
#
# EVERY launch has a matching teardown. Run `destroy` when the job is done;
# `status` prints the current spend estimate so it is never a surprise.

set -euo pipefail

PROJECT="${PROJECT:-project-ebd5a273-53ea-4c8b-81a}"
ZONE="${ZONE:-us-central1-a}"
REPO="${REPO:-https://github.com/reuellee/finite-certificates.git}"
BUCKET="${BUCKET:-gs://${PROJECT}-sweeps}"
MAX_HOURS="${MAX_HOURS:-96}"
RATE_PER_CORE_HOUR="${RATE_PER_CORE_HOUR:-0.0125}"   # n2-highcpu spot, approx

cmd="${1:?usage: launch|status|collect|stop|destroy}"
job="${2:?job name, e.g. omreal-realizability}"
vm="sweep-${job}"

case "$cmd" in
launch)
  lo="${3:?shard-lo}"; hi="${4:?shard-hi}"; cores="${5:-32}"

  # Restart rather than recreate, so preempted work resumes.
  if gcloud compute instances describe "$vm" --zone "$ZONE" --project "$PROJECT" \
       --format='value(status)' >/dev/null 2>&1; then
    echo "VM $vm exists; starting it (checkpoints on its disk are reused)."
    gcloud compute instances start "$vm" --zone "$ZONE" --project "$PROJECT"
    exit 0
  fi

  gcloud storage buckets describe "$BUCKET" --project "$PROJECT" >/dev/null 2>&1 \
    || gcloud storage buckets create "$BUCKET" --project "$PROJECT" --location=us-central1

  startup=$(mktemp)
  cat > "$startup" <<STARTUP
#!/usr/bin/env bash
set -euo pipefail
exec > >(tee -a /var/log/sweep.log) 2>&1
echo "[sweep] boot \$(date -Is)"

# Hard deadline: shut down regardless of progress. Guards against a hung
# job burning days of spot time unnoticed.
( sleep $((MAX_HOURS * 3600)); echo "[sweep] MAX_HOURS reached, halting"; \
  gsutil -q cp /var/log/sweep.log ${BUCKET}/${job}/sweep-timeout.log || true; \
  poweroff ) &

apt-get update -qq && apt-get install -y -qq python3 python3-numpy git
cd /opt
[ -d finite-certificates ] || git clone --depth 1 "$REPO" finite-certificates
cd finite-certificates

mkdir -p /opt/state
gsutil -q -m rsync -r ${BUCKET}/${job}/state /opt/state || true   # resume

python3 ops/run_shards.py --job "$job" --lo "$lo" --hi "$hi" \\
        --workers \$(nproc) --state /opt/state \\
        --out ${BUCKET}/${job} || echo "[sweep] job exited nonzero"

gsutil -q -m rsync -r /opt/state ${BUCKET}/${job}/state || true
gsutil -q cp /var/log/sweep.log ${BUCKET}/${job}/sweep.log || true
echo "[sweep] done \$(date -Is); powering off"
poweroff
STARTUP

  gcloud compute instances create "$vm" \
    --project "$PROJECT" --zone "$ZONE" \
    --machine-type "n2-highcpu-${cores}" \
    --provisioning-model=SPOT \
    --instance-termination-action=STOP \
    --image-family=debian-12 --image-project=debian-cloud \
    --boot-disk-size=50GB --boot-disk-type=pd-balanced \
    --scopes=https://www.googleapis.com/auth/devstorage.read_write \
    --metadata-from-file=startup-script="$startup" \
    --labels=purpose=research-sweep,job="$job"
  rm -f "$startup"

  echo
  echo "Launched $vm (${cores} spot cores, shards ${lo}..${hi})."
  printf 'Estimated burn: $%.2f/hour, $%.2f/day. Hard stop after %s h.\n' \
    "$(echo "$cores * $RATE_PER_CORE_HOUR" | bc -l)" \
    "$(echo "$cores * $RATE_PER_CORE_HOUR * 24" | bc -l)" "$MAX_HOURS"
  echo "TEARDOWN WHEN DONE:  $0 destroy $job"
  ;;

status)
  gcloud compute instances describe "$vm" --zone "$ZONE" --project "$PROJECT" \
    --format='table(name,status,machineType.basename(),lastStartTimestamp)' 2>/dev/null \
    || { echo "no VM named $vm (already destroyed?)"; }
  echo "--- shards completed ---"
  gcloud storage ls "${BUCKET}/${job}/state/**" 2>/dev/null | wc -l
  echo "--- recent log ---"
  gcloud compute ssh "$vm" --zone "$ZONE" --project "$PROJECT" \
    --command 'tail -n 15 /var/log/sweep.log' 2>/dev/null || true
  ;;

collect)
  dest="${3:-./sweep-results-${job}}"
  mkdir -p "$dest"
  gcloud storage rsync -r "${BUCKET}/${job}" "$dest"
  echo "results in $dest"
  ;;

stop)    gcloud compute instances stop "$vm" --zone "$ZONE" --project "$PROJECT" ;;

destroy)
  gcloud compute instances delete "$vm" --zone "$ZONE" --project "$PROJECT" --quiet
  echo "VM and boot disk deleted. Results remain in ${BUCKET}/${job}"
  echo "To remove those too:  gcloud storage rm -r ${BUCKET}/${job}"
  ;;

*) echo "unknown command: $cmd" >&2; exit 2 ;;
esac
