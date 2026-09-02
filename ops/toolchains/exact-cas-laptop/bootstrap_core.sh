#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 ABSOLUTE_INSTALL_PREFIX ABSOLUTE_DOWNLOAD_CACHE" >&2
  exit 2
fi

install_prefix=$1
download_cache=$2
case "$install_prefix:$download_cache" in
  /*:/*) ;;
  *) echo "both paths must be absolute" >&2; exit 2 ;;
esac
if [[ "$install_prefix" == / || "$download_cache" == / || "$install_prefix" == "$download_cache" ]]; then
  echo "refusing broad or overlapping targets" >&2
  exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
lock_file="$script_dir/conda-linux-64.lock"
micromamba="$download_cache/micromamba-2.8.1"
micromamba_url=https://github.com/mamba-org/micromamba-releases/releases/download/2.8.1-0/micromamba-linux-64
micromamba_sha256=9689782d863c05a1bf5d2d371ba527104e7a4eb4310c1637d8653b751aed9c82
msolve_url=https://github.com/algebraic-solving/msolve/releases/download/v0.10.1/msolve-0.10.1.tar.gz
msolve_sha256=4ea31066005dc38461fe6b85eb96828990340ce68bdc246fd37e1338d2155beb
msolve_archive="$download_cache/msolve-0.10.1.tar.gz"
msolve_build="$download_cache/msolve-0.10.1-build"
mamba_root="$download_cache/mamba-root"
jobs=${JOBS:-6}

mkdir -p -- "$download_cache"
if [[ ! -x "$micromamba" ]]; then
  curl --fail --location --retry 3 "$micromamba_url" --output "$micromamba"
  chmod 0755 "$micromamba"
fi
printf '%s  %s\n' "$micromamba_sha256" "$micromamba" | sha256sum --check

if [[ ! -d "$install_prefix/conda-meta" ]]; then
  if [[ -e "$install_prefix" ]]; then
    echo "install prefix exists but is not a conda environment: $install_prefix" >&2
    exit 2
  fi
  MAMBA_ROOT_PREFIX="$mamba_root" "$micromamba" create --yes \
    --prefix "$install_prefix" --file "$lock_file"
fi

if [[ ! -f "$msolve_archive" ]]; then
  curl --fail --location --retry 3 "$msolve_url" --output "$msolve_archive"
fi
printf '%s  %s\n' "$msolve_sha256" "$msolve_archive" | sha256sum --check

if [[ ! -x "$install_prefix/bin/msolve" ]]; then
  if [[ -e "$msolve_build" ]]; then
    echo "msolve build directory already exists: $msolve_build" >&2
    exit 2
  fi
  mkdir -- "$msolve_build"
  tar -xzf "$msolve_archive" --strip-components=1 -C "$msolve_build"
  (
    cd "$msolve_build"
    export PATH="$install_prefix/bin:/usr/bin:/bin"
    export PKG_CONFIG_PATH="$install_prefix/lib/pkgconfig"
    export CPPFLAGS="-I$install_prefix/include"
    export LDFLAGS="-L$install_prefix/lib -Wl,-rpath,$install_prefix/lib"
    ./configure --prefix="$install_prefix"
    make -j"$jobs"
    make check -j"$jobs"
    make install
  )
fi

"$script_dir/smoke_test.sh" "$install_prefix"

