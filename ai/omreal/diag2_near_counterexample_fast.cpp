// Exact finite kernel for the diagonal-two near-counterexample atlas.
//
// The proven all-parent kernel remains unchanged.  This translation unit
// includes it and adds an analysis entry point which:
//
// * reconstructs the same complete bad-signature escape-mask table;
// * verifies antipodal invariance exactly;
// * quotients signatures by rho -> -rho; and
// * enumerates every quotient pair whose escape overlap is at most a caller
//   supplied threshold.
//
// For thresholds below the minimum escape-mask size, every quotient pair
// represents exactly four unordered pairs in the unquotiented signature
// census.

#include "diag2_common_shear_fast.cpp"

namespace {

struct NearPair {
    std::uint64_t left = 0;
    std::uint64_t right = 0;
    unsigned overlap = 0;
};

std::vector<Record> reconstruct_records(
    const std::uint8_t* parent_bits,
    const std::uint64_t* topes,
    std::uint64_t tope_count,
    const std::uint8_t* entry_index,
    const std::uint8_t* replacement_index,
    const std::int8_t* sorting_sign,
    std::uint64_t& valid_count
) {
    const std::vector<std::uint64_t> signatures = enumerate_extensions(parent_bits);
    valid_count = signatures.size();

    std::unordered_set<std::uint64_t> tope_set;
    tope_set.reserve(static_cast<std::size_t>(tope_count * 2));
    for (std::uint64_t index = 0; index < tope_count; ++index) {
        if (topes[index] & ~FULL_SIGNATURE_MASK) {
            throw std::runtime_error("derived tope exceeds 56 bits");
        }
        tope_set.insert(topes[index]);
    }
    if (tope_set.size() != tope_count) {
        throw std::runtime_error("duplicate derived tope supplied");
    }

    std::vector<Record> records;
    records.reserve(signatures.size());
    for (std::uint64_t signature : signatures) {
        if (!tope_set.count(signature)) {
            records.push_back(Record{signature, EscapeMask{}, 0});
        }
    }
    if (tope_count > signatures.size()
        || records.size() != signatures.size() - static_cast<std::size_t>(tope_count)) {
        throw std::runtime_error("a derived tope is not a GP-valid extension signature");
    }

    for (unsigned ordered_shear = 0; ordered_shear < 56; ++ordered_shear) {
        std::uint64_t source_mask = 0;
        const unsigned offset = 15 * ordered_shear;
        for (unsigned entry = 0; entry < 15; ++entry) {
            source_mask |= std::uint64_t{1} << entry_index[offset + entry];
        }
        if (__builtin_popcountll(source_mask) != 15) {
            throw std::runtime_error("ordered shear does not move 15 distinct rows");
        }
        const std::uint64_t common_mask = FULL_SIGNATURE_MASK ^ source_mask;
        std::unordered_map<std::uint64_t, std::vector<std::uint64_t>> by_common;
        by_common.reserve(static_cast<std::size_t>(tope_count * 2));
        for (std::uint64_t index = 0; index < tope_count; ++index) {
            by_common[topes[index] & common_mask].push_back(topes[index] & source_mask);
        }

        for (Record& record : records) {
            std::uint64_t delete_positive = 0;
            std::uint64_t delete_negative = 0;
            for (unsigned entry = 0; entry < 15; ++entry) {
                const unsigned position = offset + entry;
                const unsigned left = entry_index[position];
                const unsigned right = replacement_index[position];
                const int left_sign = ((record.signature >> left) & 1) ? 1 : -1;
                const int right_sign = ((record.signature >> right) & 1) ? 1 : -1;
                const int alpha = -static_cast<int>(sorting_sign[position])
                    * left_sign * right_sign;
                if (alpha == 1) {
                    delete_negative |= std::uint64_t{1} << left;
                } else if (alpha == -1) {
                    delete_positive |= std::uint64_t{1} << left;
                } else {
                    throw std::runtime_error("zero transport sign");
                }
            }

            const auto found = by_common.find(record.signature & common_mask);
            bool negative_escape = true;
            bool positive_escape = true;
            if (found != by_common.end()) {
                const std::uint64_t kept_negative = source_mask ^ delete_negative;
                const std::uint64_t kept_positive = source_mask ^ delete_positive;
                for (std::uint64_t candidate : found->second) {
                    const std::uint64_t difference = candidate ^ record.signature;
                    if ((difference & kept_negative) == 0) {
                        negative_escape = false;
                    }
                    if ((difference & kept_positive) == 0) {
                        positive_escape = false;
                    }
                    if (!negative_escape && !positive_escape) {
                        break;
                    }
                }
            }
            if (negative_escape) {
                set_direction(record.mask, 2 * ordered_shear);
            }
            if (positive_escape) {
                set_direction(record.mask, 2 * ordered_shear + 1);
            }
        }
    }

    for (Record& record : records) {
        record.size = mask_size(record.mask);
    }
    return records;
}

void record_semantic_digest(
    std::vector<Record> records,
    unsigned char output[32]
) {
    std::sort(records.begin(), records.end(), [](const Record& left, const Record& right) {
        return left.signature < right.signature;
    });
    SHA256_CTX context;
    SHA256_Init(&context);
    static constexpr char prefix[] = "diag2-common-shear-records-v1\0";
    SHA256_Update(&context, prefix, sizeof(prefix) - 1);
    for (const Record& record : records) {
        sha_update_u64(context, record.signature);
        sha_update_u64(context, record.mask.low);
        sha_update_u64(context, record.mask.high);
    }
    SHA256_Final(output, &context);
}

void pair_semantic_digest(
    const std::vector<NearPair>& pairs,
    unsigned threshold,
    unsigned char output[32]
) {
    SHA256_CTX context;
    SHA256_Init(&context);
    static constexpr char prefix[] = "diag2-near-counterexample-pairs-v1\0";
    SHA256_Update(&context, prefix, sizeof(prefix) - 1);
    sha_update_u64(context, threshold);
    for (const NearPair& pair : pairs) {
        sha_update_u64(context, pair.left);
        sha_update_u64(context, pair.right);
        sha_update_u64(context, pair.overlap);
    }
    SHA256_Final(output, &context);
}

}  // namespace

extern "C" {

struct Diag2NearCounterexampleResult {
    std::uint64_t valid_count;
    std::uint64_t bad_count;
    std::uint64_t tope_count;
    std::uint64_t canonical_bad_count;
    std::uint64_t minimum_escape;
    std::uint64_t minimum_overlap;
    std::uint64_t pair_orbit_count;
    std::uint64_t raw_pair_count;
    std::uint64_t required_capacity;
    std::uint64_t overlap_histogram[113];
    unsigned char record_digest[32];
    unsigned char pair_digest[32];
};

int diag2_near_counterexample_audit(
    const std::uint8_t* parent_bits,
    const std::uint64_t* topes,
    std::uint64_t tope_count,
    const std::uint8_t* entry_index,
    const std::uint8_t* replacement_index,
    const std::int8_t* sorting_sign,
    std::uint64_t threshold,
    std::uint64_t capacity,
    std::uint64_t* pair_left,
    std::uint64_t* pair_right,
    std::uint8_t* pair_overlap,
    Diag2NearCounterexampleResult* output,
    char* error,
    std::uint64_t error_size
) {
    try {
        std::memset(output, 0, sizeof(*output));
        if (threshold > 112) {
            throw std::runtime_error("near-pair threshold exceeds 112 directions");
        }

        std::uint64_t valid_count = 0;
        std::vector<Record> records = reconstruct_records(
            parent_bits,
            topes,
            tope_count,
            entry_index,
            replacement_index,
            sorting_sign,
            valid_count
        );
        if (records.size() < 2) {
            throw std::runtime_error("fewer than two bad extension signatures");
        }

        unsigned minimum_escape = 113;
        std::unordered_map<std::uint64_t, EscapeMask> by_signature;
        by_signature.reserve(records.size() * 2);
        for (const Record& record : records) {
            minimum_escape = std::min(minimum_escape, record.size);
            by_signature.emplace(record.signature, record.mask);
        }
        if (by_signature.size() != records.size()) {
            throw std::runtime_error("duplicate bad extension signature");
        }
        if (threshold >= minimum_escape) {
            throw std::runtime_error(
                "near-pair threshold must be below the minimum escape-mask size"
            );
        }

        std::vector<Record> canonical;
        canonical.reserve(records.size() / 2);
        for (const Record& record : records) {
            const std::uint64_t antipode = FULL_SIGNATURE_MASK ^ record.signature;
            const auto found = by_signature.find(antipode);
            if (found == by_signature.end()
                || found->second.low != record.mask.low
                || found->second.high != record.mask.high) {
                throw std::runtime_error("escape masks failed antipodal invariance");
            }
            if (record.signature < antipode) {
                canonical.push_back(record);
            }
        }
        if (2 * canonical.size() != records.size()) {
            throw std::runtime_error("bad signatures did not form antipodal pairs");
        }

        std::vector<std::size_t> order(canonical.size());
        std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](std::size_t left, std::size_t right) {
            if (canonical[left].size != canonical[right].size) {
                return canonical[left].size < canonical[right].size;
            }
            return canonical[left].signature < canonical[right].signature;
        });

        unsigned minimum_overlap = minimum_escape;
        std::vector<NearPair> pairs;
        for (std::size_t left_order = 0; left_order < order.size(); ++left_order) {
            const Record& left = canonical[order[left_order]];
            if (2 * static_cast<int>(left.size) - 112 > static_cast<int>(threshold)) {
                break;
            }
            for (
                std::size_t right_order = left_order + 1;
                right_order < order.size();
                ++right_order
            ) {
                const Record& right = canonical[order[right_order]];
                if (static_cast<int>(left.size + right.size) - 112
                    > static_cast<int>(threshold)) {
                    break;
                }
                const unsigned overlap = mask_overlap(left.mask, right.mask);
                minimum_overlap = std::min(minimum_overlap, overlap);
                if (overlap <= threshold) {
                    const std::uint64_t first = std::min(left.signature, right.signature);
                    const std::uint64_t second = std::max(left.signature, right.signature);
                    pairs.push_back(NearPair{first, second, overlap});
                }
            }
        }
        std::sort(pairs.begin(), pairs.end(), [](const NearPair& left, const NearPair& right) {
            if (left.left != right.left) {
                return left.left < right.left;
            }
            return left.right < right.right;
        });
        if (std::adjacent_find(
                pairs.begin(),
                pairs.end(),
                [](const NearPair& left, const NearPair& right) {
                    return left.left == right.left && left.right == right.right;
                }
            ) != pairs.end()) {
            throw std::runtime_error("duplicate near-pair orbit");
        }

        record_semantic_digest(records, output->record_digest);
        pair_semantic_digest(pairs, static_cast<unsigned>(threshold), output->pair_digest);
        for (const NearPair& pair : pairs) {
            ++output->overlap_histogram[pair.overlap];
        }

        output->valid_count = valid_count;
        output->bad_count = records.size();
        output->tope_count = tope_count;
        output->canonical_bad_count = canonical.size();
        output->minimum_escape = minimum_escape;
        output->minimum_overlap = minimum_overlap;
        output->pair_orbit_count = pairs.size();
        output->raw_pair_count = 4 * pairs.size();
        output->required_capacity = pairs.size();

        if (pairs.size() > capacity) {
            if (error && error_size) {
                const std::string message = "near-pair output capacity is too small";
                std::strncpy(error, message.c_str(), static_cast<std::size_t>(error_size - 1));
                error[error_size - 1] = '\0';
            }
            return 2;
        }
        if (!pairs.empty() && (!pair_left || !pair_right || !pair_overlap)) {
            throw std::runtime_error("near-pair output buffers are null");
        }
        for (std::size_t index = 0; index < pairs.size(); ++index) {
            pair_left[index] = pairs[index].left;
            pair_right[index] = pairs[index].right;
            pair_overlap[index] = static_cast<std::uint8_t>(pairs[index].overlap);
        }
        return 0;
    } catch (const std::exception& exception) {
        if (error && error_size) {
            std::strncpy(error, exception.what(), static_cast<std::size_t>(error_size - 1));
            error[error_size - 1] = '\0';
        }
        return 1;
    }
}

}  // extern "C"
