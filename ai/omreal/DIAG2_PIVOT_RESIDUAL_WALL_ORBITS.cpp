// Exact Burnside census for hard residual-wall 4+5 support pairs.
//
// A first support drop from a strict five-circuit has an active rank-three
// four-support P whose determinant is one of the 13 genuine residual derived
// walls.  Pair it with a strict generic five-support R.  The private-row
// theorem fails its support-only test exactly when P union R is pencil-rigid.
//
// This program counts those (P,R) types up to S_8, separately for every
// residual wall-incidence orbit and beta stratum.  The five-support is also
// subjected to the universal unary signed filter: at least one of its five
// cofactors must be residual.  This is a necessary compatibility filter, not
// a realization or compactness theorem.
//
// The basic exact incidence/group routines are shared with the independently
// audited generic pencil-orbit verifier.  Its main is renamed and not run.

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main signed_pencil_legacy_main
#include "verify_signed_pencil_orbits.cpp"
#undef main
#pragma GCC diagnostic pop

int main() {
  // Initialize the colex triple list.
  for (int a=0;a<8;a++) for (int b=a+1;b<8;b++) for (int c=b+1;c<8;c++)
    T.push_back({a,b,c});
  sort(T.begin(),T.end(),[](auto a,auto b){
    return array<int,3>{a[2],a[1],a[0]} < array<int,3>{b[2],b[1],b[0]};
  });
  for (int i=0;i<56;i++) TI[T[i]]=i;

  // Stable representatives of all 52 four-triple incidence orbits.  The 13
  // indices in residual_ids are the genuine smooth residual walls.
  string reps="123/124/125/126 123/124/125/134 123/124/125/136 123/124/125/167 123/124/125/345 123/124/125/346 123/124/125/367 123/124/125/678 123/124/134/156 123/124/134/234 123/124/134/235 123/124/134/256 123/124/134/567 123/124/135/145 123/124/135/146 123/124/135/167 123/124/135/236 123/124/135/245 123/124/135/246 123/124/135/256 123/124/135/267 123/124/135/456 123/124/135/467 123/124/135/678 123/124/156/157 123/124/156/178 123/124/156/256 123/124/156/257 123/124/156/278 123/124/156/345 123/124/156/347 123/124/156/356 123/124/156/357 123/124/156/378 123/124/156/567 123/124/156/578 123/124/345/367 123/124/345/567 123/124/345/678 123/124/356/378 123/124/356/456 123/124/356/457 123/124/356/478 123/124/356/567 123/124/356/578 123/124/567/568 123/145/167/246 123/145/167/248 123/145/246/356 123/145/246/357 123/145/246/378 123/145/267/468";
  set<int> residual_ids={36,37,38,39,41,42,44,46,47,48,49,50,51};
  vector<uint64_t> wall_representative(52);
  stringstream representative_stream(reps); string token;
  for (int index=0; representative_stream>>token; index++) {
    wall_representative[index]=maskof(parse_support(token));
    if (residual_ids.count(index))
      residual_keys.insert(okey(parse_support(token)));
  }
  if (wall_representative.back()==0 || residual_keys.size()!=13) {
    cerr << "wrong residual representative table\n"; return 2;
  }

  // All 40,320 label permutations and their induced maps on triples.
  array<int,8> permutation={0,1,2,3,4,5,6,7};
  do {
    array<uint8_t,56> edge_map;
    for (int i=0;i<56;i++) {
      array<int,3> edge={
        permutation[T[i][0]],permutation[T[i][1]],permutation[T[i][2]]
      };
      sort(edge.begin(),edge.end()); edge_map[i]=TI[edge];
    }
    GM.push_back(edge_map);
  } while(next_permutation(permutation.begin(),permutation.end()));
  if (GM.size()!=40320) { cerr << "wrong permutation count\n"; return 2; }

  // Enumerate every strict-circuit-eligible generic size-five support and tag
  // its number of residual cofactors.
  for(int a=0;a<52;a++) for(int b=a+1;b<53;b++)
  for(int c=b+1;c<54;c++) for(int d=c+1;d<55;d++)
  for(int e=d+1;e<56;e++) {
    array<int,5> support={a,b,c,d,e};
    if(!generic5(support)) continue;
    uint64_t mask=(1ULL<<a)|(1ULL<<b)|(1ULL<<c)|(1ULL<<d)|(1ULL<<e);
    int residual_count=0;
    for(int omitted=0;omitted<5;omitted++) {
      vector<int> face;
      for(int j=0;j<5;j++) if(j!=omitted) face.push_back(support[j]);
      residual_count += residual_keys.count(okey(face));
    }
    pos[mask]=S.size(); S.push_back(attr(mask,residual_count));
  }
  if(S.size()!=2021992) { cerr << "wrong generic five-support count\n"; return 2; }

  unordered_map<int,vector<int>> fixed_cache;
  auto fixed=[&](int g)->const vector<int>& {
    auto found=fixed_cache.find(g);
    if(found!=fixed_cache.end()) return found->second;
    return fixed_cache.emplace(g,invariant(g)).first->second;
  };

  map<tuple<int,bool,int>,long long> counts;
  map<tuple<int,bool,int>,long long> fan_counts;
  map<bool,long long> totals;
  map<bool,long long> fan_totals;
  map<int,int> padding_counts;
  for(int wall_type:residual_ids) {
    Sup wall=attr(wall_representative[wall_type],1);
    vector<int> wall_edges=inds(wall.m);
    vector<int> eligible_padding;
    for(int q=0;q<56;q++) if(!(wall.m&(1ULL<<q))) {
      vector<int> support=wall_edges; support.push_back(q); sort(support.begin(),support.end());
      array<int,5> candidate{};
      copy(support.begin(),support.end(),candidate.begin());
      if(generic5(candidate)) eligible_padding.push_back(q);
    }
    padding_counts[wall_type]=eligible_padding.size();
    vector<int> stabilizer;
    for(int g=0;g<40320;g++)
      if(transform(wall.m,g)==wall.m) stabilizer.push_back(g);
    if(stabilizer.empty()) { cerr << "empty wall stabilizer\n"; return 2; }

    for(bool good:{false,true}) {
      map<int,long long> fixed_sum;
      map<int,long long> fan_fixed_sum;
      for(int g:stabilizer) {
        int fixed_padding=0;
        for(int q:eligible_padding) if(GM[g][q]==q) fixed_padding++;
        if(g==0) {
          for(auto &partner:S) if((!good||partner.k) && pencil(wall,partner)) {
            int be=beta(wall,partner); fixed_sum[be]++; fan_fixed_sum[be]+=fixed_padding;
          }
        } else for(int partner_index:fixed(g)) {
          auto &partner=S[partner_index];
          if((!good||partner.k) && pencil(wall,partner)) {
            int be=beta(wall,partner); fixed_sum[be]++; fan_fixed_sum[be]+=fixed_padding;
          }
        }
      }
      for(auto [be,value]:fixed_sum) {
        if(value%(long long)stabilizer.size()) {
          cerr << "nonintegral Burnside quotient\n"; return 2;
        }
        long long orbits=value/stabilizer.size();
        counts[{wall_type,good,be}]=orbits;
        totals[good]+=orbits;
      }
      for(auto [be,value]:fan_fixed_sum) {
        if(value%(long long)stabilizer.size()) {
          cerr << "nonintegral wall-fan Burnside quotient\n"; return 2;
        }
        long long orbits=value/stabilizer.size();
        fan_counts[{wall_type,good,be}]=orbits;
        fan_totals[good]+=orbits;
      }
    }
  }

  const vector<int> wall_order={36,37,38,39,41,42,44,46,47,48,49,50,51};
  const long long expected[2][13][4]={
    {
      {4608,2172,25,0},{4098,1512,15,0},{2165,683,5,0},
      {1891,910,33,0},{6864,4187,183,0},{2942,1331,36,0},
      {12502,5062,88,0},{3767,1921,73,0},{9193,4487,165,0},
      {390,318,21,0},{9374,4065,140,0},{15606,5558,110,0},
      {7569,3306,134,1}
    },
    {
      {4219,1917,21,0},{3891,1401,15,0},{2131,667,5,0},
      {1803,858,33,0},{6505,3867,158,0},{2887,1284,35,0},
      {12164,4930,84,0},{3417,1690,65,0},{8827,4184,145,0},
      {350,272,16,0},{8830,3786,127,0},{15233,5417,108,0},
      {7392,3180,126,1}
    }
  };
  const long long expected_totals[2]={117510,112041};
  const int expected_paddings[13]={30,48,48,30,48,48,48,34,34,52,52,52,52};
  const long long expected_fan[2][13][4]={
    {
      {136270,64281,685,0},{190279,69197,678,0},{98750,31241,219,0},
      {54999,26156,676,0},{326926,198495,8387,0},{138788,61852,1420,0},
      {593580,241081,4161,0},{127454,64278,2191,0},{309780,150810,5310,0},
      {19545,15445,959,0},{485904,209375,7134,0},{805875,286295,5339,0},
      {391806,169522,6366,29}
    },
    {
      {125101,56925,565,0},{181024,64506,678,0},{97413,30611,219,0},
      {52610,24741,676,0},{310684,183735,7274,0},{136366,59779,1372,0},
      {578757,234999,3969,0},{115652,56452,1919,0},{297666,140662,4630,0},
      {17663,13193,699,0},{457811,195021,6481,0},{786860,279047,5235,0},
      {382722,163085,6042,29}
    }
  };
  const long long expected_fan_totals[2]={5311538,5082873};
  for(int good=0;good<2;good++) {
    if(totals[bool(good)]!=expected_totals[good] ||
       fan_totals[bool(good)]!=expected_fan_totals[good]) {
      cerr << "wrong aggregate residual-wall count\n"; return 2;
    }
    for(int row=0;row<13;row++) {
      if(padding_counts[wall_order[row]]!=expected_paddings[row]) {
        cerr << "wrong residual-wall padding count\n"; return 2;
      }
      for(int be=0;be<4;be++)
      if(counts[{wall_order[row],bool(good),be}]!=expected[good][row][be] ||
         fan_counts[{wall_order[row],bool(good),be}]!=expected_fan[good][row][be]) {
        cerr << "wrong residual-wall beta stratum\n"; return 2;
      }
    }
  }

  cout << "PASS: 84,840 labeled residual four-sets form 13 S_8 wall orbits\n";
  cout << "PASS: 2,021,992 generic five-supports enumerated exactly\n";
  for(bool good:{false,true}) {
    cout << "good=" << good << " total_residual_wall_4plus5=" << totals[good]
         << " distinguished_fans=" << fan_totals[good] << "\n";
    for(int wall_type:wall_order) {
      long long subtotal=0;
      long long fan_subtotal=0;
      for(int be=0;be<=4;be++) subtotal+=counts[{wall_type,good,be}];
      for(int be=0;be<=4;be++) fan_subtotal+=fan_counts[{wall_type,good,be}];
      cout << " wall=" << wall_type << " paddings=" << padding_counts[wall_type]
           << " subtotal=" << subtotal << " fan_subtotal=" << fan_subtotal;
      for(int be=0;be<=4;be++)
        if(counts[{wall_type,good,be}])
          cout << " beta" << be << "=" << counts[{wall_type,good,be}];
      for(int be=0;be<=4;be++)
        if(fan_counts[{wall_type,good,be}])
          cout << " fanbeta" << be << "=" << fan_counts[{wall_type,good,be}];
      cout << "\n";
    }
  }
  cout << "THEOREM: these are the exact support-orbit exceptions to the flexible-spoke test\n";
  cout << "CAVEAT: good=1 is unary signed filtering, not simultaneous-wall realizability\n";
  return 0;
}
