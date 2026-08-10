// Exact finite kernel for the 2,604-parent diagonal-two common-shear screen.
//
// Python retains responsibility for reconstructing and exactly certifying the
// complete derived-arrangement topes.  This helper performs the two large but
// purely Boolean steps: enumerate every uniform single-element extension from
// the Grassmann--Pluecker constraints, and compute/test its 112-bit escape set.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <functional>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#include <openssl/sha.h>

namespace {

constexpr std::uint64_t FULL_SIGNATURE_MASK = (std::uint64_t{1} << 56) - 1;

struct Term {
    std::uint64_t variables = 0;
    std::uint8_t constant = 0;
};

struct Relation {
    std::array<Term, 3> term{};
};

struct EscapeMask {
    std::uint64_t low = 0;
    std::uint64_t high = 0;
};

struct Record {
    std::uint64_t signature = 0;
    EscapeMask mask{};
    unsigned size = 0;
};

using Subset = std::vector<int>;

std::vector<Subset> combinations(int first, int last, int size) {
    std::vector<Subset> answer;
    Subset current;
    std::function<void(int)> visit = [&](int next) {
        if (static_cast<int>(current.size()) == size) {
            answer.push_back(current);
            return;
        }
        const int needed = size - static_cast<int>(current.size());
        for (int value = next; value <= last - needed + 1; ++value) {
            current.push_back(value);
            visit(value + 1);
            current.pop_back();
        }
    };
    visit(first);
    return answer;
}

void sort_colex(std::vector<Subset>& subsets) {
    std::sort(subsets.begin(), subsets.end(), [](const Subset& left, const Subset& right) {
        for (int index = static_cast<int>(left.size()) - 1; index >= 0; --index) {
            if (left[index] != right[index]) {
                return left[index] < right[index];
            }
        }
        return false;
    });
}

std::pair<Subset, int> sorted_with_sign(Subset values) {
    int sign = 1;
    for (std::size_t index = 1; index < values.size(); ++index) {
        std::size_t cursor = index;
        while (cursor && values[cursor - 1] > values[cursor]) {
            std::swap(values[cursor - 1], values[cursor]);
            sign = -sign;
            --cursor;
        }
    }
    return {values, sign};
}

std::uint64_t subset_key(const Subset& subset) {
    std::uint64_t key = 0;
    for (int value : subset) {
        key = key * 10 + static_cast<unsigned>(value);
    }
    return key;
}

std::array<std::vector<Relation>, 56> compile_extension_system(
    const std::uint8_t* parent_bits
) {
    auto parent_bases = combinations(1, 8, 4);
    auto new_bases = combinations(1, 8, 3);
    sort_colex(parent_bases);
    sort_colex(new_bases);

    std::unordered_map<std::uint64_t, int> parent_index;
    std::unordered_map<std::uint64_t, int> new_index;
    for (int index = 0; index < static_cast<int>(parent_bases.size()); ++index) {
        parent_index.emplace(subset_key(parent_bases[index]), index);
    }
    for (int index = 0; index < static_cast<int>(new_bases.size()); ++index) {
        new_index.emplace(subset_key(new_bases[index]), index);
    }

    std::array<std::vector<Relation>, 56> by_last;
    const auto lambdas = combinations(1, 9, 2);
    for (const Subset& lambda : lambdas) {
        Subset rest;
        for (int value = 1; value <= 9; ++value) {
            if (std::find(lambda.begin(), lambda.end(), value) == lambda.end()) {
                rest.push_back(value);
            }
        }
        const auto choices = combinations(0, static_cast<int>(rest.size()) - 1, 4);
        for (const Subset& choice : choices) {
            std::array<int, 4> abcd{};
            for (int index = 0; index < 4; ++index) {
                abcd[index] = rest[choice[index]];
            }
            if (std::find(lambda.begin(), lambda.end(), 9) == lambda.end()
                && std::find(abcd.begin(), abcd.end(), 9) == abcd.end()) {
                continue;
            }

            const std::array<std::array<std::pair<int, int>, 2>, 3> pairings{{
                {{{abcd[0], abcd[1]}, {abcd[2], abcd[3]}}},
                {{{abcd[0], abcd[2]}, {abcd[1], abcd[3]}}},
                {{{abcd[0], abcd[3]}, {abcd[1], abcd[2]}}},
            }};
            const std::array<int, 3> explicit_minus{{0, 1, 0}};
            Relation relation;
            int last = -1;
            for (int term_index = 0; term_index < 3; ++term_index) {
                Term term;
                term.constant = static_cast<std::uint8_t>(explicit_minus[term_index]);
                for (const auto& pair : pairings[term_index]) {
                    Subset basis = lambda;
                    basis.push_back(pair.first);
                    basis.push_back(pair.second);
                    auto [sorted, sign] = sorted_with_sign(std::move(basis));
                    term.constant ^= static_cast<std::uint8_t>(sign < 0);
                    auto nine = std::find(sorted.begin(), sorted.end(), 9);
                    if (nine != sorted.end()) {
                        sorted.erase(nine);
                        const int variable = new_index.at(subset_key(sorted));
                        term.variables ^= std::uint64_t{1} << variable;
                        last = std::max(last, variable);
                    } else {
                        term.constant ^= parent_bits[parent_index.at(subset_key(sorted))];
                    }
                }
                relation.term[term_index] = term;
            }
            if (last < 0) {
                continue;
            }
            by_last[last].push_back(relation);
        }
    }
    return by_last;
}

bool relation_valid(const Relation& relation, std::uint64_t assignment) {
    std::array<unsigned, 3> parity{};
    for (int index = 0; index < 3; ++index) {
        parity[index] = relation.term[index].constant
            ^ static_cast<unsigned>(__builtin_parityll(
                relation.term[index].variables & assignment
            ));
    }
    return !(parity[0] == parity[1] && parity[1] == parity[2]);
}

std::vector<std::uint64_t> enumerate_extensions(const std::uint8_t* parent_bits) {
    const auto by_last = compile_extension_system(parent_bits);
    std::array<unsigned char, 56> next_value{};
    std::uint64_t assignment = 0;
    std::vector<std::uint64_t> signatures;
    signatures.reserve(100000);
    int depth = 0;
    while (true) {
        if (next_value[depth] > 1) {
            next_value[depth] = 0;
            --depth;
            if (depth < 0) {
                break;
            }
            ++next_value[depth];
            continue;
        }

        const std::uint64_t bit = std::uint64_t{1} << depth;
        if (next_value[depth]) {
            assignment |= bit;
        } else {
            assignment &= ~bit;
        }
        bool valid = true;
        for (const Relation& relation : by_last[depth]) {
            if (!relation_valid(relation, assignment)) {
                valid = false;
                break;
            }
        }
        if (!valid) {
            ++next_value[depth];
        } else if (depth == 55) {
            signatures.push_back(assignment & FULL_SIGNATURE_MASK);
            ++next_value[depth];
        } else {
            ++depth;
            next_value[depth] = 0;
        }
    }
    return signatures;
}

unsigned mask_size(const EscapeMask& mask) {
    return static_cast<unsigned>(__builtin_popcountll(mask.low)
        + __builtin_popcountll(mask.high));
}

unsigned mask_overlap(const EscapeMask& left, const EscapeMask& right) {
    return static_cast<unsigned>(__builtin_popcountll(left.low & right.low)
        + __builtin_popcountll(left.high & right.high));
}

void set_direction(EscapeMask& mask, unsigned direction) {
    if (direction < 64) {
        mask.low |= std::uint64_t{1} << direction;
    } else {
        mask.high |= std::uint64_t{1} << (direction - 64);
    }
}

void sha_update_u64(SHA256_CTX& context, std::uint64_t value) {
    std::array<unsigned char, 8> bytes{};
    for (unsigned index = 0; index < bytes.size(); ++index) {
        bytes[index] = static_cast<unsigned char>((value >> (8 * index)) & 0xff);
    }
    SHA256_Update(&context, bytes.data(), bytes.size());
}

}  // namespace

extern "C" {

struct Diag2AuditResult {
    std::uint64_t valid_count;
    std::uint64_t bad_count;
    std::uint64_t tope_count;
    std::uint64_t minimum_escape;
    std::uint64_t minimum_escape_count;
    std::uint64_t minimum_overlap;
    std::uint64_t overlap_left;
    std::uint64_t overlap_right;
    std::uint64_t overlap_left_size;
    std::uint64_t overlap_right_size;
    std::uint64_t disjoint_found;
    std::uint64_t disjoint_left;
    std::uint64_t disjoint_right;
    unsigned char record_digest[32];
};

int diag2_common_shear_audit(
    const std::uint8_t* parent_bits,
    const std::uint64_t* topes,
    std::uint64_t tope_count,
    const std::uint8_t* entry_index,
    const std::uint8_t* replacement_index,
    const std::int8_t* sorting_sign,
    Diag2AuditResult* output,
    char* error,
    std::uint64_t error_size
) {
    try {
        std::memset(output, 0, sizeof(*output));
        const std::vector<std::uint64_t> signatures = enumerate_extensions(parent_bits);
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
            || records.size()
                != signatures.size() - static_cast<std::size_t>(tope_count)) {
            throw std::runtime_error(
                "a derived tope is not a GP-valid extension signature"
            );
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

        std::array<std::uint64_t, 113> histogram{};
        for (Record& record : records) {
            record.size = mask_size(record.mask);
            ++histogram[record.size];
        }
        unsigned minimum = 113;
        for (unsigned size = 0; size <= 112; ++size) {
            if (histogram[size]) {
                minimum = size;
                break;
            }
        }
        if (minimum == 113) {
            throw std::runtime_error("no bad extension signatures were found");
        }

        std::vector<std::size_t> order(records.size());
        std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](std::size_t left, std::size_t right) {
            if (records[left].size != records[right].size) {
                return records[left].size < records[right].size;
            }
            return records[left].signature < records[right].signature;
        });

        unsigned best_overlap = 113;
        std::size_t best_left = 0;
        std::size_t best_right = 0;
        bool have_overlap = false;
        for (std::size_t left_order = 0; left_order < order.size(); ++left_order) {
            const Record& left = records[order[left_order]];
            if (have_overlap && 2 * static_cast<int>(left.size) - 112 >= static_cast<int>(best_overlap)) {
                break;
            }
            for (std::size_t right_order = left_order + 1; right_order < order.size(); ++right_order) {
                const Record& right = records[order[right_order]];
                if (have_overlap
                    && static_cast<int>(left.size + right.size) - 112 >= static_cast<int>(best_overlap)) {
                    break;
                }
                const unsigned overlap = mask_overlap(left.mask, right.mask);
                if (!have_overlap || overlap < best_overlap) {
                    best_overlap = overlap;
                    best_left = order[left_order];
                    best_right = order[right_order];
                    have_overlap = true;
                    if (overlap == 0) {
                        break;
                    }
                }
            }
            if (have_overlap && best_overlap == 0) {
                break;
            }
        }
        if (!have_overlap) {
            throw std::runtime_error("fewer than two bad extension signatures");
        }

        const std::uint64_t overlap_left_signature = records[best_left].signature;
        const std::uint64_t overlap_right_signature = records[best_right].signature;
        const unsigned overlap_left_size = records[best_left].size;
        const unsigned overlap_right_size = records[best_right].size;

        std::sort(records.begin(), records.end(), [](const Record& left, const Record& right) {
            return left.signature < right.signature;
        });
        SHA256_CTX digest_context;
        SHA256_Init(&digest_context);
        static constexpr char prefix[] = "diag2-common-shear-records-v1\0";
        SHA256_Update(&digest_context, prefix, sizeof(prefix) - 1);
        for (const Record& record : records) {
            sha_update_u64(digest_context, record.signature);
            sha_update_u64(digest_context, record.mask.low);
            sha_update_u64(digest_context, record.mask.high);
        }
        SHA256_Final(output->record_digest, &digest_context);

        output->valid_count = signatures.size();
        output->bad_count = records.size();
        output->tope_count = tope_count;
        output->minimum_escape = minimum;
        output->minimum_escape_count = histogram[minimum];
        output->minimum_overlap = best_overlap;
        output->overlap_left = overlap_left_signature;
        output->overlap_right = overlap_right_signature;
        output->overlap_left_size = overlap_left_size;
        output->overlap_right_size = overlap_right_size;
        if (best_overlap == 0) {
            output->disjoint_found = 1;
            output->disjoint_left = output->overlap_left;
            output->disjoint_right = output->overlap_right;
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
