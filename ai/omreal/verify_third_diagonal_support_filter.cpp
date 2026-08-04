// Exact generic single-piece filter for the third diagonal.
//
// A cofinal circuit-cover index is a five-set Q of triples on eight labels.
// The common-apex lemma kills H_c^2(C_{rho,Q}) whenever delta(Q) >= 3;
// omission kills it as well.  On a generic parent-derived-wall stratum, an
// all-unit five-circuit cannot be positive for a realizable extension.  This
// checker enumerates the supports which survive all three necessary tests:
//
//   (1) Q covers all eight labels;
//   (2) delta(Q) <= 2; and
//   (3) at least one circuit cofactor is a residual derived-wall atom.
//
// It also computes beta(Q)=4-rank(D_Q), the remaining weight-gauge dimension,
// and exact S_8 orbit counts.  This is a finite reduction, not a vanishing
// theorem: nongeneric residual-wall and smaller-support faces still have to be
// attached, and the retained generic loci still require topology.

#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;

vector<array<int,3>> triples;
map<array<int,3>,int> triple_index;
set<array<uint8_t,16>> residual_keys;

vector<int> parse_support(const string& text) {
  vector<int> out;
  stringstream stream(text);
  string token;
  while (getline(stream, token, '/')) {
    array<int,3> edge = {token[0]-'1', token[1]-'1', token[2]-'1'};
    sort(edge.begin(), edge.end());
    out.push_back(triple_index[edge]);
  }
  return out;
}

array<uint8_t,16> four_orbit_key(const vector<int>& edges) {
  array<uint8_t,16> best;
  best.fill(255);
  array<int,4> permutation = {0,1,2,3};
  do {
    array<uint8_t,16> candidate{};
    for (int vertex=0; vertex<8; ++vertex) {
      int mask=0;
      for (int j=0; j<4; ++j) {
        const auto& edge=triples[edges[j]];
        if (find(edge.begin(), edge.end(), vertex) != edge.end())
          mask |= 1 << permutation[j];
      }
      candidate[mask]++;
    }
    best=min(best,candidate);
  } while (next_permutation(permutation.begin(),permutation.end()));
  return best;
}

bool generic_five(const array<int,5>& edges) {
  int degrees[8]={};
  int codegrees[8][8]={};
  for (int edge_index:edges) {
    const auto& edge=triples[edge_index];
    for (int vertex:edge)
      if (++degrees[vertex] >= 4) return false;
    for (int i=0;i<3;++i) for (int j=i+1;j<3;++j)
      if (++codegrees[edge[i]][edge[j]] >= 3) return false;
  }
  return true;
}

uint64_t mask_of(const array<int,5>& edges) {
  uint64_t mask=0;
  for (int edge:edges) mask |= 1ULL << edge;
  return mask;
}

int residual_count(const array<int,5>& edges) {
  int count=0;
  for (int omitted=0;omitted<5;++omitted) {
    vector<int> four;
    for (int j=0;j<5;++j) if (j!=omitted) four.push_back(edges[j]);
    count += residual_keys.count(four_orbit_key(four));
  }
  return count;
}

array<int,8> degrees_of(const array<int,5>& edges) {
  array<int,8> degrees{};
  for (int edge_index:edges)
    for (int vertex:triples[edge_index]) degrees[vertex]++;
  return degrees;
}

int delta_of(const array<int,5>& edges) {
  int best=0;
  for (int apex=0;apex<8;++apex) {
    int dominated=0;
    for (int moving=0;moving<8;++moving) if (moving!=apex) {
      bool good=true;
      for (int edge_index:edges) {
        const auto& edge=triples[edge_index];
        bool has_moving=find(edge.begin(),edge.end(),moving)!=edge.end();
        bool has_apex=find(edge.begin(),edge.end(),apex)!=edge.end();
        if (has_moving && !has_apex) { good=false; break; }
      }
      dominated += good;
    }
    best=max(best,dominated);
  }
  return min(3,best);
}

int rank_centered(const array<int,5>& edges) {
  array<array<int,8>,4> rows{};
  array<int,8> base{};
  for (int vertex:triples[edges[0]]) base[vertex]=1;
  for (int i=1;i<5;++i) {
    for (int vertex:triples[edges[i]]) rows[i-1][vertex]++;
    for (int vertex=0;vertex<8;++vertex) rows[i-1][vertex]-=base[vertex];
  }
  // Exact rank modulo p.  Each centered incidence row has squared Euclidean
  // norm at most six, so Hadamard bounds every square minor of order at most
  // four by (sqrt(6))^4=36.  The prime below is larger than that bound;
  // consequently no nonzero integer minor can disappear modulo p.
  constexpr int prime=65521;
  int rank=0;
  for (int column=0;column<8 && rank<4;++column) {
    int pivot=rank;
    while (pivot<4 && (rows[pivot][column]%prime+prime)%prime==0) pivot++;
    if (pivot==4) continue;
    swap(rows[pivot],rows[rank]);
    int value=(rows[rank][column]%prime+prime)%prime;
    int inverse=1;
    for (int exponent=prime-2,base=value;exponent;exponent>>=1) {
      if (exponent&1) inverse=(long long)inverse*base%prime;
      base=(long long)base*base%prime;
    }
    for (int j=column;j<8;++j)
      rows[rank][j]=(long long)(rows[rank][j]%prime+prime)%prime*inverse%prime;
    for (int i=0;i<4;++i) if (i!=rank) {
      int factor=(rows[i][column]%prime+prime)%prime;
      if (!factor) continue;
      for (int j=column;j<8;++j)
        rows[i][j]=((rows[i][j]%prime+prime)%prime
                    -(long long)factor*rows[rank][j])%prime;
    }
    rank++;
  }
  return rank;
}

uint64_t transform(uint64_t mask,const array<uint8_t,56>& edge_map) {
  uint64_t out=0;
  while(mask) {
    int edge=__builtin_ctzll(mask);
    out |= 1ULL << edge_map[edge];
    mask &= mask-1;
  }
  return out;
}

string support_text(uint64_t mask) {
  string out;
  while(mask) {
    int edge_index=__builtin_ctzll(mask);
    if (!out.empty()) out += '/';
    for (int vertex:triples[edge_index]) out += char('1'+vertex);
    mask &= mask-1;
  }
  return out;
}

int main() {
  for (int a=0;a<8;++a) for (int b=a+1;b<8;++b)
    for (int c=b+1;c<8;++c) triples.push_back({a,b,c});
  // Match the colexicographic order used by the other exact checkers.
  sort(triples.begin(),triples.end(),[](auto left,auto right) {
    return array<int,3>{left[2],left[1],left[0]}
         < array<int,3>{right[2],right[1],right[0]};
  });
  for (int i=0;i<56;++i) triple_index[triples[i]]=i;

  // The 13 residual four-normal wall types among the 52 nonzero S_8 orbits.
  string representatives=
    "123/124/125/126 123/124/125/134 123/124/125/136 "
    "123/124/125/167 123/124/125/345 123/124/125/346 "
    "123/124/125/367 123/124/125/678 123/124/134/156 "
    "123/124/134/234 123/124/134/235 123/124/134/256 "
    "123/124/134/567 123/124/135/145 123/124/135/146 "
    "123/124/135/167 123/124/135/236 123/124/135/245 "
    "123/124/135/246 123/124/135/256 123/124/135/267 "
    "123/124/135/456 123/124/135/467 123/124/135/678 "
    "123/124/156/157 123/124/156/178 123/124/156/256 "
    "123/124/156/257 123/124/156/278 123/124/156/345 "
    "123/124/156/347 123/124/156/356 123/124/156/357 "
    "123/124/156/378 123/124/156/567 123/124/156/578 "
    "123/124/345/367 123/124/345/567 123/124/345/678 "
    "123/124/356/378 123/124/356/456 123/124/356/457 "
    "123/124/356/478 123/124/356/567 123/124/356/578 "
    "123/124/567/568 123/145/167/246 123/145/167/248 "
    "123/145/246/356 123/145/246/357 123/145/246/378 "
    "123/145/267/468";
  set<int> residual_indices={36,37,38,39,41,42,44,46,47,48,49,50,51};
  stringstream rep_stream(representatives);
  string token;
  int rep_index=0;
  while(rep_stream>>token) {
    if (residual_indices.count(rep_index))
      residual_keys.insert(four_orbit_key(parse_support(token)));
    rep_index++;
  }
  if (rep_index!=52 || residual_keys.size()!=13) {
    cerr << "wrong residual-wall table\n";
    return 2;
  }

  map<tuple<int,int,int>,long long> labeled; // delta,beta,residual count
  unordered_set<uint64_t> retained;
  retained.reserve(1000000);
  long long generic=0, covers=0, killed_delta=0, killed_unit=0;
  for (int a=0;a<52;++a) for (int b=a+1;b<53;++b)
    for (int c=b+1;c<54;++c) for (int d=c+1;d<55;++d)
      for (int e=d+1;e<56;++e) {
        array<int,5> support={a,b,c,d,e};
        if (!generic_five(support)) continue;
        generic++;
        auto degrees=degrees_of(support);
        if (*min_element(degrees.begin(),degrees.end())==0) continue;
        covers++;
        int delta=delta_of(support);
        if (delta>=3) { killed_delta++; continue; }
        int residuals=residual_count(support);
        if (!residuals) { killed_unit++; continue; }
        int beta=4-rank_centered(support);
        labeled[{delta,beta,residuals}]++;
        retained.insert(mask_of(support));
      }

  // Exact orbit extraction.  Only the retained set is materialized.
  vector<array<uint8_t,56>> group_maps;
  array<int,8> permutation={0,1,2,3,4,5,6,7};
  do {
    array<uint8_t,56> edge_map{};
    for (int i=0;i<56;++i) {
      array<int,3> edge={permutation[triples[i][0]],
                         permutation[triples[i][1]],
                         permutation[triples[i][2]]};
      sort(edge.begin(),edge.end());
      edge_map[i]=triple_index[edge];
    }
    group_maps.push_back(edge_map);
  } while(next_permutation(permutation.begin(),permutation.end()));

  map<pair<int,int>,long long> orbit_count; // delta,beta
  vector<tuple<uint64_t,int,int>> canonical_representatives;
  while(!retained.empty()) {
    uint64_t representative=*retained.begin();
    array<int,5> support{};
    int at=0;
    uint64_t cursor=representative;
    while(cursor) {
      support[at++]=__builtin_ctzll(cursor);
      cursor&=cursor-1;
    }
    int delta=delta_of(support);
    int beta=4-rank_centered(support);
    orbit_count[{delta,beta}]++;
    uint64_t canonical=~uint64_t(0);
    for (const auto& edge_map:group_maps) {
      uint64_t image=transform(representative,edge_map);
      canonical=min(canonical,image);
      retained.erase(image);
    }
    canonical_representatives.push_back({canonical,delta,beta});
  }

  // Frozen expected values make this an exact regression certificate.
  const map<tuple<int,int,int>,long long> expected_labeled={
    {{1,0,3},20160}, {{1,0,4},5040}, {{1,0,5},40320},
    {{2,0,1},58800}, {{2,0,2},260400}, {{2,0,3},272160},
    {{2,0,4},15120}, {{2,0,5},85680}, {{2,1,4},2520}
  };
  const map<pair<int,int>,long long> expected_orbits={
    {{1,0},5}, {{2,0},39}, {{2,1},1}
  };
  if (generic!=2021992 || covers!=1099560 || killed_delta!=339360
      || killed_unit!=0 || labeled!=expected_labeled
      || orbit_count!=expected_orbits) {
    cerr << "wrong third-diagonal support census\n";
    return 2;
  }
  cout << "generic=" << generic << " covers=" << covers
       << " killed_delta=" << killed_delta
       << " killed_all_unit=" << killed_unit << "\n";
  long long total=0;
  for (auto [key,count]:labeled) {
    auto [delta,beta,residuals]=key;
    cout << "labeled delta=" << delta << " beta=" << beta
         << " residuals=" << residuals << " count=" << count << "\n";
    total+=count;
  }
  long long orbits=0;
  for (auto [key,count]:orbit_count) {
    cout << "orbits delta=" << key.first << " beta=" << key.second
         << " count=" << count << "\n";
    orbits+=count;
  }
  sort(canonical_representatives.begin(),canonical_representatives.end());
  vector<string> representative_texts;
  for (auto [mask,delta,beta]:canonical_representatives) {
    array<int,5> support{};
    int at=0;
    uint64_t cursor=mask;
    while(cursor) {
      support[at++]=__builtin_ctzll(cursor);
      cursor&=cursor-1;
    }
    string text=support_text(mask);
    representative_texts.push_back(text);
    cout << "REP delta=" << delta << " beta=" << beta
         << " residuals=" << residual_count(support)
         << " support=" << text << "\n";
  }
  // Stable cross-language fingerprint used by the sparse-stabilizer checker.
  // Hash the lexicographically sorted canonical support strings, each with a
  // trailing newline, using 64-bit FNV-1a.
  sort(representative_texts.begin(),representative_texts.end());
  uint64_t fingerprint=14695981039346656037ULL;
  for(const string& line:representative_texts) {
    for(unsigned char byte:line) {
      fingerprint^=byte;
      fingerprint*=1099511628211ULL;
    }
    fingerprint^=static_cast<unsigned char>('\n');
    fingerprint*=1099511628211ULL;
  }
  if(fingerprint!=0x2b0dace2b3066b2eULL) {
    cerr << "wrong canonical-representative fingerprint\n";
    return 2;
  }
  cout << "REPRESENTATIVE_FNV64=2b0dace2b3066b2e\n";
  if (total!=760200 || orbits!=45) {
    cerr << "wrong aggregate survivor count\n";
    return 2;
  }
  cout << "SURVIVORS: labeled=" << total << " orbits=" << orbits << "\n";
  cout << "PASS: exact generic third-diagonal single-piece reduction\n";
  return 0;
}
