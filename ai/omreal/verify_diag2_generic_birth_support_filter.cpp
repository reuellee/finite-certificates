// Exact low-source support filter for diagonal-two support drops.
//
// A residual support drop supplies a positive wall circuit P.  Its active
// support has size four at an ordinary wall and size three at a localization
// wall.  The main residue pairs P with a support-minimal size-five partner R;
// the verifier also exhausts every size-four partner at ordinary walls.  For an
// ordered column shear e -> f put
//
//   m(e,f) = #{I in P: e in I, f notin I}
//          + #{I in R: e in I, f notin I},
//
// counting a triple twice when it belongs to both colored supports.  The
// moving-witness lemma makes the shear automatically compatible when
// m(e,f) <= 1.  Hence every selected witness-pair obstruction must satisfy
// m(e,f) >= 2 for all 56 ordered pairs.  This verifier classifies that exact
// unsigned necessary condition for the 3+5, 4+5, and ordinary-wall 4+4
// cases.
//
// The inherited predicate generic5 is not a generic-position assumption.
// It rejects exactly two patterns which cannot be a minimal five-circuit:
// four triples containing one label give four normals in that column's
// three-dimensional annihilator, while three triples containing one label
// pair give three normals in that parent two-plane's two-dimensional
// annihilator.  Thus a rejected support has a dependent proper subset.  The
// exhaustive count below pins both sides of this minimality filter.
//
// The verifier deliberately makes no claim about the
// XOR transport signs, full witness polytopes, geometric wall realizability,
// or diagonal two.

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#define main signed_pencil_legacy_main
#include "verify_signed_pencil_orbits.cpp"
#undef main
#pragma GCC diagnostic pop

namespace {

using Counts = array<uint8_t, 56>;

Counts source_counts(uint64_t support) {
  Counts answer{};
  for (int edge : inds(support)) {
    for (int source : T[edge]) {
      for (int target = 0; target < 8; ++target) {
        if (target == source || find(T[edge].begin(), T[edge].end(), target) != T[edge].end())
          continue;
        const int bit = 7 * source + target - (target > source);
        ++answer[bit];
      }
    }
  }
  return answer;
}

bool source_hard(const Counts &left, const Counts &right) {
  for (int bit = 0; bit < 56; ++bit)
    if (left[bit] + right[bit] < 2) return false;
  return true;
}

string support_text(uint64_t support) {
  string answer;
  for (int edge : inds(support)) {
    if (!answer.empty()) answer += '/';
    for (int vertex : T[edge]) answer += char('1' + vertex);
  }
  return answer;
}

}  // namespace

int main() {
  for (int a = 0; a < 8; ++a)
    for (int b = a + 1; b < 8; ++b)
      for (int c = b + 1; c < 8; ++c) T.push_back({a, b, c});
  sort(T.begin(), T.end(), [](auto a, auto b) {
    return array<int, 3>{a[2], a[1], a[0]} < array<int, 3>{b[2], b[1], b[0]};
  });
  for (int index = 0; index < 56; ++index) TI[T[index]] = index;

  const string representative_text =
      "123/124/125/126 123/124/125/134 123/124/125/136 123/124/125/167 "
      "123/124/125/345 123/124/125/346 123/124/125/367 123/124/125/678 "
      "123/124/134/156 123/124/134/234 123/124/134/235 123/124/134/256 "
      "123/124/134/567 123/124/135/145 123/124/135/146 123/124/135/167 "
      "123/124/135/236 123/124/135/245 123/124/135/246 123/124/135/256 "
      "123/124/135/267 123/124/135/456 123/124/135/467 123/124/135/678 "
      "123/124/156/157 123/124/156/178 123/124/156/256 123/124/156/257 "
      "123/124/156/278 123/124/156/345 123/124/156/347 123/124/156/356 "
      "123/124/156/357 123/124/156/378 123/124/156/567 123/124/156/578 "
      "123/124/345/367 123/124/345/567 123/124/345/678 123/124/356/378 "
      "123/124/356/456 123/124/356/457 123/124/356/478 123/124/356/567 "
      "123/124/356/578 123/124/567/568 123/145/167/246 123/145/167/248 "
      "123/145/246/356 123/145/246/357 123/145/246/378 123/145/267/468";
  const set<int> ordinary_types = {37, 38, 41, 42, 44, 48, 49, 50, 51};
  const set<int> localization_types = {36, 39, 46, 47};
  vector<uint64_t> wall_representative(52);
  stringstream representatives(representative_text);
  string token;
  for (int type = 0; representatives >> token; ++type)
    wall_representative[type] = maskof(parse_support(token));
  if (!wall_representative.back()) {
    cerr << "wrong residual representative table\n";
    return 2;
  }

  // The actual positive circuit at a localization wall omits the displayed
  // residual normal.  These are the exact certificates from
  // verify_derived_wall_sides.py, relabeled to the representatives above.
  const map<int, uint64_t> localization_circuit = {
      {36, maskof(parse_support("123/345/367"))},
      {39, maskof(parse_support("123/356/378"))},
      {46, maskof(parse_support("123/145/167"))},
      {47, maskof(parse_support("123/145/167"))},
  };

  const string expected_ordinary_text =
      "37:146/247/258/368/178 "
      "41:137/267/348/258/168 41:137/267/238/158/468 "
      "44:145/347/267/248/168 "
      "48:257/367/348/268/178 48:257/467/348/268/178 "
      "49:247/167/148/258/368 49:256/467/248/368/178 "
      "49:347/167/258/368/178 49:347/567/258/368/178 "
      "49:156/147/458/368/278 49:347/167/138/568/278 "
      "49:136/147/348/568/278 49:123/167/348/568/278 "
      "49:124/167/348/568/278 49:134/167/348/568/278 "
      "49:234/167/348/568/278 49:125/167/348/568/278 "
      "49:235/167/348/568/278 49:126/167/348/568/278 "
      "49:136/167/348/568/278 49:236/167/348/568/278 "
      "49:146/167/348/568/278 49:246/167/348/568/278 "
      "49:346/167/348/568/278 49:156/167/348/568/278 "
      "49:256/167/348/568/278 49:356/167/348/568/278 "
      "49:456/167/348/568/278 49:167/267/348/568/278 "
      "49:167/367/348/568/278 49:136/127/348/258/678 "
      "49:156/127/348/258/678 "
      "50:356/247/167/148/258 50:356/457/167/148/258 "
      "50:345/147/567/258/168 50:346/147/567/258/168 "
      "50:356/257/467/458/168 50:347/567/258/368/178 "
      "50:257/367/358/168/478 "
      "51:356/347/157/138/258 51:123/356/347/258/178 "
      "51:124/356/347/258/178 51:134/356/347/258/178 "
      "51:234/356/347/258/178 51:135/356/347/258/178 "
      "51:235/356/347/258/178 51:346/356/347/258/178 "
      "51:356/347/157/258/178 51:234/136/357/258/178 "
      "51:234/356/357/258/178 51:356/347/357/258/178 "
      "51:256/247/367/358/178";
  const map<int, string> expected_localization = {
      {36, "156/247/258/468/178"},
      {39, "146/457/267/248/158"},
      {46, "256/347/358/468/278"},
      {47, "256/347/358/468/278"},
  };
  const map<int, long long> expected_five_raw = {
      {36, 8}, {37, 8}, {38, 0}, {39, 8}, {41, 8}, {42, 0},
      {44, 4}, {46, 8}, {47, 8}, {48, 48}, {49, 96}, {50, 22},
      {51, 76},
  };
  const map<int, long long> expected_four_raw = {
      {37, 0}, {38, 0}, {41, 0}, {42, 0}, {44, 0},
      {48, 0}, {49, 2}, {50, 0}, {51, 1},
  };
  const map<int, string> expected_four_representative = {
      {49, "167/348/568/278"},
      {51, "356/347/258/178"},
  };
  map<int, vector<uint64_t>> expected_ordinary;
  stringstream expected_stream(expected_ordinary_text);
  while (expected_stream >> token) {
    const size_t colon = token.find(':');
    if (colon == string::npos) {
      cerr << "malformed expected representative\n";
      return 2;
    }
    const int type = stoi(token.substr(0, colon));
    expected_ordinary[type].push_back(
        maskof(parse_support(token.substr(colon + 1))));
  }

  array<int, 8> permutation = {0, 1, 2, 3, 4, 5, 6, 7};
  do {
    array<uint8_t, 56> edge_map;
    for (int index = 0; index < 56; ++index) {
      array<int, 3> edge = {
          permutation[T[index][0]], permutation[T[index][1]], permutation[T[index][2]]};
      sort(edge.begin(), edge.end());
      edge_map[index] = TI[edge];
    }
    GM.push_back(edge_map);
  } while (next_permutation(permutation.begin(), permutation.end()));
  if (GM.size() != 40320) {
    cerr << "wrong permutation count\n";
    return 2;
  }

  vector<uint64_t> partners;
  vector<Counts> partner_counts;
  long long five_total = 0;
  long long structurally_nonminimal_five = 0;
  for (int a = 0; a < 52; ++a)
    for (int b = a + 1; b < 53; ++b)
      for (int c = b + 1; c < 54; ++c)
        for (int d = c + 1; d < 55; ++d)
          for (int e = d + 1; e < 56; ++e) {
            ++five_total;
            array<int, 5> support = {a, b, c, d, e};
            if (!generic5(support)) {
              ++structurally_nonminimal_five;
              continue;
            }
            uint64_t mask = (1ULL << a) | (1ULL << b) | (1ULL << c) |
                            (1ULL << d) | (1ULL << e);
            partners.push_back(mask);
            partner_counts.push_back(source_counts(mask));
          }
  if (five_total != 3819816 || structurally_nonminimal_five != 1797824 ||
      partners.size() != 2021992) {
    cerr << "wrong minimal-five eligibility count\n";
    return 2;
  }

  vector<uint64_t> four_partners;
  vector<Counts> four_partner_counts;
  for (int a = 0; a < 53; ++a)
    for (int b = a + 1; b < 54; ++b)
      for (int c = b + 1; c < 55; ++c)
        for (int d = c + 1; d < 56; ++d) {
          uint64_t mask = (1ULL << a) | (1ULL << b) | (1ULL << c) |
                          (1ULL << d);
          four_partners.push_back(mask);
          four_partner_counts.push_back(source_counts(mask));
        }
  if (four_partners.size() != 367290) {
    cerr << "wrong four-support count\n";
    return 2;
  }

  map<int, long long> raw_counts;
  map<int, vector<uint64_t>> hard_partners;
  for (int type : ordinary_types) {
    const Counts wall_counts = source_counts(wall_representative[type]);
    for (size_t index = 0; index < partners.size(); ++index) {
      if (!source_hard(wall_counts, partner_counts[index])) continue;
      ++raw_counts[type];
      hard_partners[type].push_back(partners[index]);
    }
  }
  for (int type : localization_types) {
    const Counts wall_counts = source_counts(localization_circuit.at(type));
    for (size_t index = 0; index < partners.size(); ++index) {
      if (!source_hard(wall_counts, partner_counts[index])) continue;
      ++raw_counts[type];
      hard_partners[type].push_back(partners[index]);
    }
  }
  map<int, long long> raw_four_counts;
  map<int, vector<uint64_t>> hard_four_partners;
  for (int type : ordinary_types) {
    const Counts wall_counts = source_counts(wall_representative[type]);
    for (size_t index = 0; index < four_partners.size(); ++index) {
      if (!source_hard(wall_counts, four_partner_counts[index])) continue;
      ++raw_four_counts[type];
      hard_four_partners[type].push_back(four_partners[index]);
    }
  }

  // Quotient ordinary partners by the stabilizer of the decorated wall
  // support.  The lexicographically smallest integer mask is retained as the
  // deterministic representative of each orbit.
  map<int, vector<uint64_t>> orbit_representatives;
  for (int type : ordinary_types) {
    vector<int> stabilizer;
    for (int group = 0; group < 40320; ++group)
      if (transform(wall_representative[type], group) == wall_representative[type])
        stabilizer.push_back(group);
    set<uint64_t> remaining(hard_partners[type].begin(), hard_partners[type].end());
    while (!remaining.empty()) {
      const uint64_t seed = *remaining.begin();
      uint64_t canonical = seed;
      for (int group : stabilizer) canonical = min(canonical, transform(seed, group));
      orbit_representatives[type].push_back(canonical);
      for (int group : stabilizer) remaining.erase(transform(seed, group));
    }
    sort(orbit_representatives[type].begin(), orbit_representatives[type].end());
  }

  for (const auto &[type, count] : expected_five_raw) {
    if (raw_counts[type] != count) {
      cerr << "source-hard labeled count changed for type " << type << "\n";
      return 1;
    }
  }
  for (const auto &[type, count] : expected_four_raw) {
    if (raw_four_counts[type] != count) {
      cerr << "source-hard four-partner count changed for type " << type << "\n";
      return 1;
    }
  }
  for (int type : ordinary_types) {
    if (orbit_representatives[type] != expected_ordinary[type]) {
      cerr << "ordinary orbit representatives changed for type " << type << "\n";
      return 1;
    }
  }
  for (int type : localization_types) {
    vector<int> stabilizer;
    for (int group = 0; group < 40320; ++group)
      if (transform(localization_circuit.at(type), group) == localization_circuit.at(type))
        stabilizer.push_back(group);
    set<uint64_t> remaining(hard_partners[type].begin(), hard_partners[type].end());
    while (!remaining.empty()) {
      const uint64_t seed = *remaining.begin();
      uint64_t canonical = seed;
      for (int group : stabilizer) canonical = min(canonical, transform(seed, group));
      orbit_representatives[type].push_back(canonical);
      for (int group : stabilizer) remaining.erase(transform(seed, group));
    }
    sort(orbit_representatives[type].begin(), orbit_representatives[type].end());
  }
  for (int type : localization_types) {
    const vector<uint64_t> expected = {
        maskof(parse_support(expected_localization.at(type)))};
    if (orbit_representatives[type] != expected) {
      cerr << "active localization orbit changed for type " << type
           << ": got";
      for (uint64_t support : orbit_representatives[type])
        cerr << ' ' << support_text(support);
      cerr << "; expected " << expected_localization.at(type) << "\n";
      return 1;
    }
  }

  map<int, vector<uint64_t>> four_orbit_representatives;
  for (int type : ordinary_types) {
    vector<int> stabilizer;
    for (int group = 0; group < 40320; ++group)
      if (transform(wall_representative[type], group) == wall_representative[type])
        stabilizer.push_back(group);
    set<uint64_t> remaining(
        hard_four_partners[type].begin(), hard_four_partners[type].end());
    while (!remaining.empty()) {
      const uint64_t seed = *remaining.begin();
      uint64_t canonical = seed;
      for (int group : stabilizer) canonical = min(canonical, transform(seed, group));
      four_orbit_representatives[type].push_back(canonical);
      for (int group : stabilizer) remaining.erase(transform(seed, group));
    }
    sort(
        four_orbit_representatives[type].begin(),
        four_orbit_representatives[type].end());
    vector<uint64_t> expected;
    if (expected_four_representative.count(type))
      expected.push_back(maskof(parse_support(expected_four_representative.at(type))));
    if (four_orbit_representatives[type] != expected) {
      cerr << "ordinary four-partner orbits changed for type " << type << "\n";
      return 1;
    }
  }

  cout << "PASS minimal-five eligibility total=" << five_total
       << " eligible=" << partners.size()
       << " structurally-nonminimal=" << structurally_nonminimal_five << "\n";
  long long ordinary_orbits = 0;
  for (int type : ordinary_types) {
    ordinary_orbits += orbit_representatives[type].size();
    cout << "ordinary " << type << " raw=" << raw_counts[type]
         << " orbits=" << orbit_representatives[type].size() << "\n";
    for (uint64_t support : orbit_representatives[type])
      cout << "  " << support_text(support) << "\n";
  }
  long long localization_raw = 0;
  for (int type : localization_types) {
    localization_raw += raw_counts[type];
    cout << "localization " << type << " raw=" << raw_counts[type]
         << " active-circuit-orbits=" << orbit_representatives[type].size() << "\n";
    for (uint64_t support : orbit_representatives[type])
      cout << "  " << support_text(support) << "\n";
  }
  long long four_raw = 0;
  long long four_orbits = 0;
  for (int type : ordinary_types) {
    four_raw += raw_four_counts[type];
    four_orbits += four_orbit_representatives[type].size();
    cout << "ordinary-four-partner " << type << " raw=" << raw_four_counts[type]
         << " orbits=" << four_orbit_representatives[type].size() << "\n";
    for (uint64_t support : four_orbit_representatives[type])
      cout << "  " << support_text(support) << "\n";
  }
  cout << "SUMMARY ordinary_orbits=" << ordinary_orbits
       << " localization_raw=" << localization_raw
       << " four_partner_raw=" << four_raw
       << " four_partner_orbits=" << four_orbits << "\n";
  if (ordinary_orbits != 53 || localization_raw != 32 ||
      four_raw != 3 || four_orbits != 2) {
    cerr << "support-drop source-hard summary changed\n";
    return 1;
  }
  return 0;
}
