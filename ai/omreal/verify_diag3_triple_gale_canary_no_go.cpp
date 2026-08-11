#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

// Necessary-test replay for the correctly homogenized Gale pullbacks of the
// six hard diagonal-three triples in all 40,320 S8 frames.  The Mersenne prime
// is larger than the rigorous L1 coefficient bound 12*96^3 = 10,616,832 for
// a sum/difference of two Jacobian minors.  Therefore a true integer
// parent-bracket product cannot disappear through its scalar coefficient.
static constexpr uint32_t P = 2147483647u;
static constexpr int NV = 9;
static constexpr int NS = 7;
static constexpr int NB = 62;

static inline uint32_t addm(uint32_t a, uint32_t b) {
    uint64_t value = uint64_t(a) + b;
    value = (value & P) + (value >> 31);
    if (value >= P) value -= P;
    return uint32_t(value);
}

static inline uint32_t subm(uint32_t a, uint32_t b) {
    return a >= b ? a - b : uint32_t(uint64_t(a) + P - b);
}

static inline uint32_t mulm(uint32_t a, uint32_t b) {
    uint64_t value = uint64_t(a) * b;
    value = (value & P) + (value >> 31);
    value = (value & P) + (value >> 31);
    if (value >= P) value -= P;
    return uint32_t(value);
}

static uint32_t powm(uint32_t value, uint32_t exponent) {
    uint32_t answer = 1;
    while (exponent) {
        if (exponent & 1) answer = mulm(answer, value);
        value = mulm(value, value);
        exponent >>= 1;
    }
    return answer;
}

static inline uint32_t invm(uint32_t value) {
    assert(value);
    return powm(value, P - 2);
}

struct Term {
    uint32_t exponent;
    int8_t coefficient;
};

struct Family {
    std::vector<uint32_t> offset;
    std::vector<Term> term;
    size_t size() const { return offset.empty() ? 0 : offset.size() - 1; }
};

template <typename T>
static T read_scalar(std::ifstream &input) {
    T value;
    input.read(reinterpret_cast<char *>(&value), sizeof(value));
    if (!input) throw std::runtime_error("truncated input");
    return value;
}

static Family read_family(std::ifstream &input) {
    uint32_t count = read_scalar<uint32_t>(input);
    uint32_t terms = read_scalar<uint32_t>(input);
    Family result;
    result.offset.resize(size_t(count) + 1);
    input.read(reinterpret_cast<char *>(result.offset.data()),
               std::streamsize(result.offset.size() * sizeof(uint32_t)));
    if (!input || result.offset.back() != terms)
        throw std::runtime_error("bad polynomial offsets");
    result.term.reserve(terms);
    for (uint32_t index = 0; index < terms; ++index) {
        Term term;
        term.exponent = read_scalar<uint32_t>(input);
        term.coefficient = read_scalar<int8_t>(input);
        result.term.push_back(term);
    }
    return result;
}

static uint64_t splitmix64(uint64_t &state) {
    uint64_t value = (state += 0x9e3779b97f4a7c15ULL);
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

using Point = std::array<uint32_t, NV>;

static uint32_t coefficient_mod(int8_t coefficient) {
    int value = int(coefficient);
    return value >= 0 ? uint32_t(value) : uint32_t(int64_t(P) + value);
}

static void evaluate_value_gradient(
    const Family &family, size_t polynomial, const Point &point,
    const Point &inverse, uint32_t &value, std::array<uint32_t, NV> &gradient
) {
    value = 0;
    gradient.fill(0);
    for (uint32_t ti = family.offset[polynomial];
         ti < family.offset[polynomial + 1]; ++ti) {
        const Term &term = family.term[ti];
        uint32_t term_value = coefficient_mod(term.coefficient);
        for (int variable = 0; variable < NV; ++variable) {
            unsigned exponent = (term.exponent >> (2 * variable)) & 3u;
            for (unsigned copy = 0; copy < exponent; ++copy)
                term_value = mulm(term_value, point[variable]);
        }
        value = addm(value, term_value);
        for (int variable = 0; variable < NV; ++variable) {
            unsigned exponent = (term.exponent >> (2 * variable)) & 3u;
            if (!exponent) continue;
            uint32_t derivative = mulm(term_value, inverse[variable]);
            derivative = mulm(derivative, exponent);
            gradient[variable] = addm(gradient[variable], derivative);
        }
    }
}

static int rref(std::vector<std::vector<uint32_t>> &matrix,
                std::vector<int> &pivot_columns) {
    int rows = int(matrix.size());
    int columns = rows ? int(matrix[0].size()) : 0;
    int rank = 0;
    for (int column = 0; column < columns && rank < rows; ++column) {
        int pivot = rank;
        while (pivot < rows && matrix[pivot][column] == 0) ++pivot;
        if (pivot == rows) continue;
        std::swap(matrix[pivot], matrix[rank]);
        uint32_t scale = invm(matrix[rank][column]);
        for (int here = column; here < columns; ++here)
            matrix[rank][here] = mulm(matrix[rank][here], scale);
        for (int row = 0; row < rows; ++row) {
            if (row == rank || !matrix[row][column]) continue;
            uint32_t factor = matrix[row][column];
            for (int here = column; here < columns; ++here)
                matrix[row][here] = subm(
                    matrix[row][here], mulm(factor, matrix[rank][here]));
        }
        pivot_columns.push_back(column);
        ++rank;
    }
    return rank;
}

struct SampleData {
    std::array<Point, NS> point;
    std::array<Point, NS> inverse;
    std::array<uint32_t, NS * NV> lambda;
};

static bool construct_samples(
    const Family &brackets, uint64_t seed, SampleData &samples
) {
    uint64_t state = seed;
    for (int sample = 0; sample < NS; ++sample) {
        bool accepted = false;
        for (int attempt = 0; attempt < 10000 && !accepted; ++attempt) {
            Point point, inverse;
            for (int variable = 0; variable < NV; ++variable) {
                point[variable] = uint32_t(splitmix64(state) % (P - 1)) + 1;
                inverse[variable] = invm(point[variable]);
            }
            accepted = true;
            for (size_t bracket = 0; bracket < brackets.size(); ++bracket) {
                uint32_t value;
                std::array<uint32_t, NV> gradient;
                evaluate_value_gradient(
                    brackets, bracket, point, inverse, value, gradient);
                if (!value) {
                    accepted = false;
                    break;
                }
            }
            if (accepted) {
                samples.point[sample] = point;
                samples.inverse[sample] = inverse;
            }
        }
        if (!accepted) throw std::runtime_error("could not find generic point");
    }

    // The transpose of the sampled bracket dlog matrix is 62 by 63.
    std::vector<std::vector<uint32_t>> transpose(
        NB, std::vector<uint32_t>(NS * NV));
    for (int sample = 0; sample < NS; ++sample) {
        for (int bracket = 0; bracket < NB; ++bracket) {
            uint32_t value;
            std::array<uint32_t, NV> gradient;
            evaluate_value_gradient(
                brackets, bracket, samples.point[sample],
                samples.inverse[sample], value, gradient);
            uint32_t inverse_value = invm(value);
            for (int variable = 0; variable < NV; ++variable)
                transpose[bracket][sample * NV + variable] =
                    mulm(gradient[variable], inverse_value);
        }
    }
    std::vector<int> pivot_columns;
    int rank = rref(transpose, pivot_columns);
    if (rank != NB) return false;
    std::array<bool, NS * NV> pivot{};
    for (int column : pivot_columns) pivot[column] = true;
    int free_column = -1;
    for (int column = 0; column < NS * NV; ++column)
        if (!pivot[column]) {
            free_column = column;
            break;
        }
    if (free_column < 0) throw std::runtime_error("missing null coordinate");
    samples.lambda.fill(0);
    samples.lambda[free_column] = 1;
    for (int row = 0; row < NB; ++row) {
        int column = pivot_columns[row];
        samples.lambda[column] = transpose[row][free_column]
            ? P - transpose[row][free_column] : 0;
    }
    return true;
}

struct FactorEvaluations {
    std::vector<uint32_t> gradient;
    std::vector<uint32_t> directional_gradient;
};

static FactorEvaluations evaluate_factors(
    const Family &factors, const SampleData &samples
) {
    size_t entries = factors.size() * NS * NV;
    FactorEvaluations result;
    result.gradient.assign(entries, 0);
    result.directional_gradient.assign(entries, 0);

    uint64_t maximum_derivative_l1 = 0;
    for (size_t factor = 0; factor < factors.size(); ++factor) {
        std::array<uint64_t, NV> derivative_l1{};
        for (uint32_t ti = factors.offset[factor];
             ti < factors.offset[factor + 1]; ++ti) {
            const Term &term = factors.term[ti];
            for (int variable = 0; variable < NV; ++variable) {
                unsigned exponent = (term.exponent >> (2 * variable)) & 3u;
                derivative_l1[variable] +=
                    uint64_t(std::abs(int(term.coefficient))) * exponent;
            }
        }
        maximum_derivative_l1 = std::max(
            maximum_derivative_l1,
            *std::max_element(derivative_l1.begin(), derivative_l1.end()));

        for (int sample = 0; sample < NS; ++sample) {
            uint32_t *gradient = result.gradient.data()
                + (factor * NS + sample) * NV;
            uint32_t *directional = result.directional_gradient.data()
                + (factor * NS + sample) * NV;
            for (uint32_t ti = factors.offset[factor];
                 ti < factors.offset[factor + 1]; ++ti) {
                const Term &term = factors.term[ti];
                uint32_t term_value = coefficient_mod(term.coefficient);
                for (int variable = 0; variable < NV; ++variable) {
                    unsigned exponent =
                        (term.exponent >> (2 * variable)) & 3u;
                    for (unsigned copy = 0; copy < exponent; ++copy)
                        term_value = mulm(
                            term_value, samples.point[sample][variable]);
                }
                uint32_t weighted = 0;
                for (int variable = 0; variable < NV; ++variable) {
                    unsigned exponent =
                        (term.exponent >> (2 * variable)) & 3u;
                    if (!exponent) continue;
                    uint32_t contribution = mulm(
                        samples.lambda[sample * NV + variable],
                        samples.inverse[sample][variable]);
                    contribution = mulm(contribution, exponent);
                    weighted = addm(weighted, contribution);
                }
                for (int variable = 0; variable < NV; ++variable) {
                    unsigned exponent =
                        (term.exponent >> (2 * variable)) & 3u;
                    if (!exponent) continue;
                    uint32_t derivative = mulm(
                        term_value, samples.inverse[sample][variable]);
                    derivative = mulm(derivative, exponent);
                    gradient[variable] = addm(gradient[variable], derivative);
                    uint32_t correction = mulm(
                        samples.lambda[sample * NV + variable],
                        samples.inverse[sample][variable]);
                    uint32_t second = mulm(
                        derivative, subm(weighted, correction));
                    directional[variable] = addm(
                        directional[variable], second);
                }
            }
        }
    }
    if (maximum_derivative_l1 != 96)
        throw std::runtime_error("unexpected derivative L1 bound");
    if (6 * maximum_derivative_l1 * maximum_derivative_l1
            * maximum_derivative_l1 >= P)
        throw std::runtime_error("prime does not dominate coefficient bound");
    std::cerr << "FACTOR_EVALUATIONS=" << factors.size()
              << " derivative_l1=" << maximum_derivative_l1 << "\n";
    return result;
}

struct Triple {
    uint16_t factor[3];
};

struct Candidate {
    uint16_t factor[3];
    uint8_t left[3];
    uint8_t right[3];
    int8_t sign;
};

static std::vector<Triple> read_triples(
    const std::string &path, uint64_t limit
) {
    std::ifstream input(path, std::ios::binary);
    uint32_t count = read_scalar<uint32_t>(input);
    if (limit && limit < count) count = uint32_t(limit);
    std::vector<Triple> triples(count);
    input.read(reinterpret_cast<char *>(triples.data()),
               std::streamsize(triples.size() * sizeof(Triple)));
    if (!input) throw std::runtime_error("truncated triple file");
    return triples;
}

static std::vector<Candidate> scan(
    const std::vector<Triple> &triples, const FactorEvaluations &evaluation
) {
    if (sizeof(Triple) != 6) throw std::runtime_error("padded triple record");
    std::array<std::array<int, NV>, NV> pair_index;
    for (auto &row : pair_index) row.fill(-1);
    int pair_count = 0;
    for (int left = 0; left < NV; ++left)
        for (int right = left + 1; right < NV; ++right) {
            pair_index[left][right] = pair_index[right][left] = pair_count++;
        }
    struct MinorIndex { uint8_t i, j, k, ij, ik, jk; };
    std::vector<MinorIndex> minors;
    for (int i = 0; i < NV; ++i)
        for (int j = i + 1; j < NV; ++j)
            for (int k = j + 1; k < NV; ++k)
                minors.push_back(MinorIndex{
                    uint8_t(i), uint8_t(j), uint8_t(k),
                    uint8_t(pair_index[i][j]), uint8_t(pair_index[i][k]),
                    uint8_t(pair_index[j][k])});
    if (pair_count != 36 || minors.size() != 84)
        throw std::runtime_error("bad coordinate combinatorics");
    struct ShearIndex { uint8_t left, right; int8_t sign; };
    std::vector<ShearIndex> shears;
    for (size_t left = 0; left < minors.size(); ++left) {
        std::array<int, NV> present{};
        present[minors[left].i] = present[minors[left].j] =
            present[minors[left].k] = 1;
        for (size_t right = left + 1; right < minors.size(); ++right) {
            int overlap = present[minors[right].i] + present[minors[right].j]
                + present[minors[right].k];
            if (overlap != 2) continue;
            shears.push_back(ShearIndex{uint8_t(left), uint8_t(right), 1});
            shears.push_back(ShearIndex{uint8_t(left), uint8_t(right), -1});
        }
    }
    if (shears.size() != 1512)
        throw std::runtime_error("bad shear combinatorics");

    std::vector<std::pair<size_t, size_t>> buckets;
    for (size_t begin = 0; begin < triples.size();) {
        size_t end = begin + 1;
        while (end < triples.size()
               && triples[end].factor[0] == triples[begin].factor[0]
               && triples[end].factor[1] == triples[begin].factor[1])
            ++end;
        buckets.emplace_back(begin, end);
        begin = end;
    }
    std::vector<Candidate> candidates;
    uint64_t minor_tested = 0, minor_survivors = 0, shear_tested = 0;

#pragma omp parallel
    {
        std::vector<Candidate> local;
        uint64_t local_minor_tested = 0, local_minor_survivors = 0;
        uint64_t local_shear_tested = 0;
#pragma omp for schedule(dynamic, 1)
        for (size_t bucket = 0; bucket < buckets.size(); ++bucket) {
            size_t begin = buckets[bucket].first;
            size_t end = buckets[bucket].second;
            uint16_t first = triples[begin].factor[0];
            uint16_t second = triples[begin].factor[1];
            std::array<std::array<uint32_t, 36>, NS> wedge{};
            std::array<std::array<uint32_t, 36>, NS> directional_wedge{};
            for (int sample = 0; sample < NS; ++sample) {
                const uint32_t *g1 = evaluation.gradient.data()
                    + (size_t(first) * NS + sample) * NV;
                const uint32_t *g2 = evaluation.gradient.data()
                    + (size_t(second) * NS + sample) * NV;
                const uint32_t *d1 = evaluation.directional_gradient.data()
                    + (size_t(first) * NS + sample) * NV;
                const uint32_t *d2 = evaluation.directional_gradient.data()
                    + (size_t(second) * NS + sample) * NV;
                int pi = 0;
                for (int i = 0; i < NV; ++i)
                    for (int j = i + 1; j < NV; ++j, ++pi) {
                        wedge[sample][pi] = subm(
                            mulm(g1[i], g2[j]), mulm(g1[j], g2[i]));
                        uint32_t positive = addm(
                            mulm(d1[i], g2[j]), mulm(g1[i], d2[j]));
                        uint32_t negative = addm(
                            mulm(d1[j], g2[i]), mulm(g1[j], d2[i]));
                        directional_wedge[sample][pi] =
                            subm(positive, negative);
                    }
            }

            for (size_t row = begin; row < end; ++row) {
                uint16_t third = triples[row].factor[2];
                std::array<std::array<uint32_t, NS>, 84> minor_value{};
                std::array<std::array<uint32_t, NS>, 84> minor_derivative{};
                for (size_t mi = 0; mi < minors.size(); ++mi) {
                    const MinorIndex &minor = minors[mi];
                    for (int sample = 0; sample < NS; ++sample) {
                        const uint32_t *g = evaluation.gradient.data()
                            + (size_t(third) * NS + sample) * NV;
                        const uint32_t *d =
                            evaluation.directional_gradient.data()
                            + (size_t(third) * NS + sample) * NV;
                        uint32_t positive = addm(
                            mulm(wedge[sample][minor.ij], g[minor.k]),
                            mulm(wedge[sample][minor.jk], g[minor.i]));
                        minor_value[mi][sample] = subm(
                            positive,
                            mulm(wedge[sample][minor.ik], g[minor.j]));
                        uint32_t dpositive = addm(
                            addm(
                                mulm(
                                    directional_wedge[sample][minor.ij],
                                    g[minor.k]),
                                mulm(wedge[sample][minor.ij], d[minor.k])),
                            addm(
                                mulm(
                                    directional_wedge[sample][minor.jk],
                                    g[minor.i]),
                                mulm(wedge[sample][minor.jk], d[minor.i])));
                        uint32_t dnegative = addm(
                            mulm(
                                directional_wedge[sample][minor.ik],
                                g[minor.j]),
                            mulm(wedge[sample][minor.ik], d[minor.j]));
                        minor_derivative[mi][sample] =
                            subm(dpositive, dnegative);
                    }
                }
                for (size_t mi = 0; mi < minors.size(); ++mi) {
                    bool zero = false;
                    for (int sample = 0; sample < NS; ++sample)
                        zero = zero || !minor_value[mi][sample];
                    ++local_minor_tested;
                    if (zero) continue;
                    std::array<uint32_t, NS + 1> prefix, suffix;
                    prefix[0] = 1;
                    for (int sample = 0; sample < NS; ++sample)
                        prefix[sample + 1] = mulm(
                            prefix[sample], minor_value[mi][sample]);
                    suffix[NS] = 1;
                    for (int sample = NS - 1; sample >= 0; --sample)
                        suffix[sample] = mulm(
                            suffix[sample + 1], minor_value[mi][sample]);
                    uint32_t relation = 0;
                    for (int sample = 0; sample < NS; ++sample)
                        relation = addm(
                            relation,
                            mulm(
                                minor_derivative[mi][sample],
                                mulm(prefix[sample], suffix[sample + 1])));
                    if (!relation) ++local_minor_survivors;
                }
                for (const ShearIndex &shear : shears) {
                    std::array<uint32_t, NS> value, derivative;
                    bool zero = false;
                    for (int sample = 0; sample < NS; ++sample) {
                        if (shear.sign > 0) {
                            value[sample] = addm(
                                minor_value[shear.left][sample],
                                minor_value[shear.right][sample]);
                            derivative[sample] = addm(
                                minor_derivative[shear.left][sample],
                                minor_derivative[shear.right][sample]);
                        } else {
                            value[sample] = subm(
                                minor_value[shear.left][sample],
                                minor_value[shear.right][sample]);
                            derivative[sample] = subm(
                                minor_derivative[shear.left][sample],
                                minor_derivative[shear.right][sample]);
                        }
                        if (!value[sample]) { zero = true; break; }
                    }
                    ++local_shear_tested;
                    if (zero) continue;
                    std::array<uint32_t, NS + 1> prefix, suffix;
                    prefix[0] = 1;
                    for (int sample = 0; sample < NS; ++sample)
                        prefix[sample + 1] = mulm(
                            prefix[sample], value[sample]);
                    suffix[NS] = 1;
                    for (int sample = NS - 1; sample >= 0; --sample)
                        suffix[sample] = mulm(
                            suffix[sample + 1], value[sample]);
                    uint32_t relation = 0;
                    for (int sample = 0; sample < NS; ++sample)
                        relation = addm(
                            relation,
                            mulm(
                                derivative[sample],
                                mulm(prefix[sample], suffix[sample + 1])));
                    if (!relation) {
                        const MinorIndex &left = minors[shear.left];
                        const MinorIndex &right = minors[shear.right];
                        Candidate candidate{
                            {triples[row].factor[0], triples[row].factor[1],
                             triples[row].factor[2]},
                            {left.i, left.j, left.k},
                            {right.i, right.j, right.k}, shear.sign};
                        local.push_back(candidate);
                    }
                }
            }
        }
#pragma omp critical
        {
            minor_tested += local_minor_tested;
            minor_survivors += local_minor_survivors;
            shear_tested += local_shear_tested;
            candidates.insert(candidates.end(), local.begin(), local.end());
        }
    }
    std::cerr << "MINORS_TESTED=" << minor_tested
              << " MODULAR_SURVIVORS=" << minor_survivors << "\n";
    std::cerr << "SHEARS_TESTED=" << shear_tested
              << " MODULAR_SURVIVORS=" << candidates.size() << "\n";
    if (minor_tested != 20321280ull || minor_survivors != 0 ||
        shear_tested != 365783040ull || !candidates.empty())
        throw std::runtime_error("corrected Gale canary no-go census changed");
    return candidates;
}

static void write_candidates(
    const std::string &path, std::vector<Candidate> candidates
) {
    std::sort(candidates.begin(), candidates.end(), [](const auto &left,
                                                       const auto &right) {
        return std::memcmp(&left, &right, sizeof(Candidate)) < 0;
    });
    std::ofstream output(path, std::ios::binary);
    uint64_t count = candidates.size();
    output.write(reinterpret_cast<const char *>(&count), sizeof(count));
    for (const Candidate &candidate : candidates) {
        output.write(reinterpret_cast<const char *>(candidate.factor), 6);
        output.write(reinterpret_cast<const char *>(candidate.left), 3);
        output.write(reinterpret_cast<const char *>(candidate.right), 3);
        output.write(reinterpret_cast<const char *>(&candidate.sign), 1);
    }
}

int main(int argc, char **argv) {
    if (argc < 4 || argc > 6) {
        std::cerr << "usage: gale_no_go POLYDB TRIPLES OUTPUT [LIMIT] [SEED]\n";
        return 2;
    }
    uint64_t limit = argc >= 5 ? std::stoull(argv[4]) : 0;
    uint64_t seed = argc >= 6 ? std::stoull(argv[5]) : 0xD1A63004ULL;
    auto started = std::chrono::steady_clock::now();
    std::ifstream input(argv[1], std::ios::binary);
    char magic[8];
    input.read(magic, 8);
    if (!input || std::memcmp(magic, "D3MWPOL1", 8) != 0)
        throw std::runtime_error("bad polynomial database magic");
    Family factors = read_family(input);
    Family brackets = read_family(input);
    if (factors.size() != 26740 || brackets.size() != NB)
        throw std::runtime_error("bad polynomial database dimensions");
    SampleData samples;
    for (int retry = 0; !construct_samples(brackets, seed + retry, samples);
         ++retry) {
        if (retry > 100) throw std::runtime_error("dlog rank never reached 62");
    }
    std::cerr << "DLOG_RANK=62 NULLITY=1 PRIME=" << P
              << " SAMPLES=" << NS << "\n";
    FactorEvaluations evaluation = evaluate_factors(factors, samples);
    std::vector<Triple> triples = read_triples(argv[2], limit);
    std::cerr << "TRIPLES=" << triples.size() << "\n";
    if (triples.size() != 241920)
        throw std::runtime_error("corrected Gale canary-frame count changed");
    std::vector<Candidate> candidates = scan(triples, evaluation);
    write_candidates(argv[3], std::move(candidates));
    double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    std::cerr << "SECONDS=" << seconds << "\n";
    return 0;
}
