// Exact S_8 Burnside verifier for pencil-rigid generic 4+5 and 5+5
// derived-circuit support pairs on eight labels.
//
// A size-five support is retained by the universal signed structural filter
// precisely when at least one of its five cofactors is a residual derived-wall
// atom.  The program reports both the unsigned census (good=0) and this
// signed-filtered census (good=1), stratified by
//
//   beta = sum_Q (|Q|-1) - rank_Q(D_H),
//
// where D_H stacks the centered triple-incidence rows of the two supports.
// Ordered 5+5 orbits and the swap Burnside term are computed separately;
// their average is the unordered S_8 orbit count.  Equal supports are allowed.
// All incidence and group computations are exact.

#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
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

struct Sup { uint64_t m, defect; array<uint8_t,8> deg; uint8_t k; };
vector<array<int,3>> T;
map<array<int,3>,int> TI;
vector<array<uint8_t,56>> GM;
unordered_map<uint64_t,int> pos;
vector<Sup> S;
set<array<uint8_t,16>> residual_keys;

array<uint8_t,16> okey(const vector<int>& es){
  array<uint8_t,16> best; best.fill(255);
  array<int,4> p={0,1,2,3};
  do {
    array<uint8_t,16> c{};
    for(int v=0;v<8;v++){
      int mask=0;
      for(int j=0;j<4;j++){
        auto &e=T[es[j]];
        if(e[0]==v||e[1]==v||e[2]==v) mask|=1<<p[j];
      }
      c[mask]++;
    }
    if(c<best) best=c;
  } while(next_permutation(p.begin(),p.end()));
  return best;
}
vector<int> parse_support(string s){
  vector<int> out; stringstream ss(s); string x;
  while(getline(ss,x,'/')){
    array<int,3> e={x[0]-'1',x[1]-'1',x[2]-'1'};
    sort(e.begin(),e.end()); out.push_back(TI[e]);
  }
  return out;
}
uint64_t maskof(const vector<int>& e){uint64_t m=0;for(int x:e)m|=1ULL<<x;return m;}
vector<int> inds(uint64_t m){vector<int> z;while(m){int i=__builtin_ctzll(m);z.push_back(i);m&=m-1;}return z;}
uint64_t transform(uint64_t m,int gi){uint64_t z=0;while(m){int i=__builtin_ctzll(m);z|=1ULL<<GM[gi][i];m&=m-1;}return z;}
bool generic5(const array<int,5>& e){
  int d[8]={},c[8][8]={};
  for(int q:e){for(int x:T[q])if(++d[x]>=4)return false;for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(++c[T[q][i]][T[q][j]]>=3)return false;}
  return true;
}
Sup attr(uint64_t m,uint8_t k){
  Sup s{};s.m=m;s.k=k;uint64_t cover=0;
  for(int q:inds(m))for(int v:T[q]){s.deg[v]++;for(int f=0;f<8;f++)if(find(T[q].begin(),T[q].end(),f)==T[q].end()){int bit=7*v+f-(f>v);cover|=1ULL<<bit;}}
  s.defect=((1ULL<<56)-1)^cover;return s;
}
bool pencil(const Sup&a,const Sup&b){
  if(a.defect&b.defect)return false;array<int,8>d{};uint64_t u=a.m|b.m;
  for(int q:inds(u))for(int v:T[q])d[v]++;
  return *min_element(d.begin(),d.end())>=3;
}
int beta(const Sup&a,const Sup&b){
  vector<array<int,8>> rows;
  for(uint64_t m:{a.m,b.m}){
    auto q=inds(m);array<int,8> base{};for(int v:T[q[0]])base[v]=1;
    for(int z=1;z<(int)q.size();z++){array<int,8> r{};for(int v:T[q[z]])r[v]++;for(int v=0;v<8;v++)r[v]-=base[v];rows.push_back(r);}
  }
  // Exact rank mod p: every row has norm <=sqrt(6), so every square minor
  // has absolute value <=6^4=1296 < p.  Reduction mod p preserves Q-rank.
  const int P=65521;int rank=0;
  for(int col=0;col<8&&rank<(int)rows.size();col++){
    int piv=rank;while(piv<(int)rows.size()&&((rows[piv][col]%P)+P)%P==0)piv++;
    if(piv==(int)rows.size())continue;swap(rows[piv],rows[rank]);
    int a=((rows[rank][col]%P)+P)%P,inv=1,e=P-2,b=a;while(e){if(e&1)inv=(long long)inv*b%P;b=(long long)b*b%P;e>>=1;}
    for(int j=col;j<8;j++)rows[rank][j]=(long long)(((rows[rank][j]%P)+P)%P)*inv%P;
    for(int i=0;i<(int)rows.size();i++)if(i!=rank){int f=((rows[i][col]%P)+P)%P;if(f)for(int j=col;j<8;j++)rows[i][j]=(((rows[i][j]%P)+P)%P-(long long)f*rows[rank][j])%P;}
    rank++;
  }
  return (int)rows.size()-rank;
}
vector<int> invariant(int gi){
  bool seen[56]={};vector<pair<int,uint64_t>> cy;
  for(int i=0;i<56;i++)if(!seen[i]){int j=i,n=0;uint64_t m=0;while(!seen[j]){seen[j]=1;n++;m|=1ULL<<j;j=GM[gi][j];}cy.push_back({n,m});}
  vector<int> out;
  function<void(int,int,uint64_t)> rec=[&](int st,int left,uint64_t m){if(!left){auto it=pos.find(m);if(it!=pos.end())out.push_back(it->second);return;}for(int z=st;z<(int)cy.size();z++)if(cy[z].first<=left)rec(z+1,left-cy[z].first,m|cy[z].second);};
  rec(0,5,0);return out;
}
string pkey(const array<int,8>&p){string s;for(int x:p)s.push_back(char(x));return s;}
int main(){
  for(int a=0;a<8;a++)for(int b=a+1;b<8;b++)for(int c=b+1;c<8;c++)T.push_back({a,b,c});
  sort(T.begin(),T.end(),[](auto a,auto b){return array<int,3>{a[2],a[1],a[0]}<array<int,3>{b[2],b[1],b[0]};});
  for(int i=0;i<56;i++)TI[T[i]]=i;
  string reps="123/124/125/126 123/124/125/134 123/124/125/136 123/124/125/167 123/124/125/345 123/124/125/346 123/124/125/367 123/124/125/678 123/124/134/156 123/124/134/234 123/124/134/235 123/124/134/256 123/124/134/567 123/124/135/145 123/124/135/146 123/124/135/167 123/124/135/236 123/124/135/245 123/124/135/246 123/124/135/256 123/124/135/267 123/124/135/456 123/124/135/467 123/124/135/678 123/124/156/157 123/124/156/178 123/124/156/256 123/124/156/257 123/124/156/278 123/124/156/345 123/124/156/347 123/124/156/356 123/124/156/357 123/124/156/378 123/124/156/567 123/124/156/578 123/124/345/367 123/124/345/567 123/124/345/678 123/124/356/378 123/124/356/456 123/124/356/457 123/124/356/478 123/124/356/567 123/124/356/578 123/124/567/568 123/145/167/246 123/145/167/248 123/145/246/356 123/145/246/357 123/145/246/378 123/145/267/468";
  set<int> ri={36,37,38,39,41,42,44,46,47,48,49,50,51};stringstream rs(reps);string x;int ix=0;while(rs>>x){if(ri.count(ix))residual_keys.insert(okey(parse_support(x)));ix++;}
  array<int,8> p={0,1,2,3,4,5,6,7};map<string,int> pidx;vector<array<int,8>> perms;
  do{perms.push_back(p);pidx[pkey(p)]=perms.size()-1;array<uint8_t,56> mp;for(int i=0;i<56;i++){array<int,3> e={p[T[i][0]],p[T[i][1]],p[T[i][2]]};sort(e.begin(),e.end());mp[i]=TI[e];}GM.push_back(mp);}while(next_permutation(p.begin(),p.end()));
  for(int a=0;a<52;a++)for(int b=a+1;b<53;b++)for(int c=b+1;c<54;c++)for(int d=c+1;d<55;d++)for(int e=d+1;e<56;e++){
    array<int,5> q={a,b,c,d,e};if(!generic5(q))continue;uint64_t m=(1ULL<<a)|(1ULL<<b)|(1ULL<<c)|(1ULL<<d)|(1ULL<<e);int k=0;for(int z=0;z<5;z++){vector<int> f;for(int j=0;j<5;j++)if(j!=z)f.push_back(q[j]);k+=residual_keys.count(okey(f));}pos[m]=S.size();S.push_back(attr(m,k));
  }
  if(S.size()!=2021992){cerr<<"wrong generic size-five support count\n";return 2;}
  unordered_set<uint64_t> rem;rem.reserve(S.size()*2);for(auto&s:S)rem.insert(s.m);
  vector<int> R;vector<vector<int>> H;
  while(!rem.empty()){
    uint64_t m=*rem.begin();R.push_back(pos[m]);vector<int> h;
    for(int g=0;g<(int)GM.size();g++){uint64_t z=transform(m,g);rem.erase(z);if(z==m)h.push_back(g);}H.push_back(move(h));
  }
  if(R.size()!=117){cerr<<"wrong generic size-five orbit count\n";return 2;}
  unordered_map<int,vector<int>> ficache;
  auto fixed=[&](int g)->const vector<int>&{auto it=ficache.find(g);if(it!=ficache.end())return it->second;return ficache.emplace(g,invariant(g)).first->second;};
  auto idcount=[&](const Sup&a,bool good){long long n=0;for(auto&b:S)if((!good||b.k)&&pencil(a,b))n++;return n;};
  map<bool,long long> ordered,swapterm;map<pair<int,bool>,long long> cross;map<pair<bool,int>,long long> ob,sb;map<tuple<int,bool,int>,long long> cb;
  for(bool good:{false,true}){
    long long total=0;
    for(int z=0;z<(int)R.size();z++){auto&a=S[R[z]];if(good&&!a.k)continue;map<int,long long> num;for(auto&b:S)if((!good||b.k)&&pencil(a,b))num[beta(a,b)]++;for(int g:H[z])if(g)for(int bi:fixed(g)){auto&b=S[bi];if((!good||b.k)&&pencil(a,b))num[beta(a,b)]++;}for(auto [be,n]:num){if(n%H[z].size()){cerr<<"nonint\n";return 2;}ob[{good,be}]+=n/H[z].size();total+=n/H[z].size();}}
    ordered[good]=total;
  }
  // conjugacy representatives
  map<vector<int>,int> classrep,classcount;
  for(int g=0;g<(int)perms.size();g++){bool seen[8]={};vector<int> ct;for(int i=0;i<8;i++)if(!seen[i]){int j=i,n=0;while(!seen[j]){seen[j]=1;n++;j=perms[g][j];}ct.push_back(n);}sort(ct.rbegin(),ct.rend());classrep.try_emplace(ct,g);classcount[ct]++;}
  for(bool good:{false,true}){map<int,long long> num;for(auto &[ct,g]:classrep){array<int,8> sq;for(int i=0;i<8;i++)sq[i]=perms[g][perms[g][i]];int g2=pidx[pkey(sq)];const vector<int>*vv=nullptr;vector<int> all;if(g2==0){all.resize(S.size());iota(all.begin(),all.end(),0);vv=&all;}else vv=&fixed(g2);map<int,long long> n;for(int ai:*vv){auto&a=S[ai];if(good&&!a.k)continue;auto&b=S[pos[transform(a.m,g)]];if(pencil(a,b))n[beta(a,b)]++;}for(auto [be,v]:n)num[be]+=1LL*classcount[ct]*v;}for(auto [be,v]:num){sb[{good,be}]=v/40320;swapterm[good]+=v/40320;}}
  // hard-coded valid four reps A,B
  vector<uint64_t> q4={maskof(parse_support("123/124/135/167")),maskof(parse_support("123/124/156/178"))};
  for(int qt=0;qt<2;qt++){Sup a=attr(q4[qt],1);vector<int> h;for(int g=0;g<40320;g++)if(transform(a.m,g)==a.m)h.push_back(g);for(bool good:{false,true}){map<int,long long> num;for(auto&b:S)if((!good||b.k)&&pencil(a,b))num[beta(a,b)]++;for(int g:h)if(g)for(int bi:fixed(g)){auto&b=S[bi];if((!good||b.k)&&pencil(a,b))num[beta(a,b)]++;}for(auto [be,n]:num){cb[{qt,good,be}]=n/h.size();cross[{qt,good}]+=n/h.size();}}}
  if(ordered[false]!=9388292||swapterm[false]!=4532||cross[{0,false}]!=3114||cross[{1,false}]!=1511||
     ordered[true]!=7617613||swapterm[true]!=4011||cross[{0,true}]!=2805||cross[{1,true}]!=1455){
    cerr<<"wrong pencil-rigid aggregate orbit count\n";return 2;
  }
  const long long expected55[2][5][2]={
    {{0,0},{8216425,2501},{1155559,1841},{16302,186},{6,4}},
    {{0,0},{6726123,2259},{880582,1596},{10905,153},{3,3}}
  };
  const long long expected45[2][2][5]={
    {{968,1922,224,0,0},{497,911,100,3,0}},
    {{925,1700,180,0,0},{494,876,83,2,0}}
  };
  for(int good=0;good<2;good++)for(int be=0;be<5;be++){
    if(ob[{bool(good),be}]!=expected55[good][be][0]||sb[{bool(good),be}]!=expected55[good][be][1]){
      cerr<<"wrong beta-stratified 5+5 count\n";return 2;
    }
  }
  for(int good=0;good<2;good++)for(int qt=0;qt<2;qt++)for(int be=0;be<5;be++){
    if(cb[{qt,bool(good),be}]!=expected45[good][qt][be]){
      cerr<<"wrong beta-stratified 4+5 count\n";return 2;
    }
  }
  cout<<"PASS: 2,021,992 generic size-five supports form 117 S_8 orbits\n";
  for(bool good:{false,true}){
    cout<<"good="<<good<<" ordered55="<<ordered[good]<<" swap="<<swapterm[good]
        <<" unordered55="<<(ordered[good]+swapterm[good])/2
        <<" A5="<<cross[{0,good}]<<" B5="<<cross[{1,good}]<<"\n";
    for(int be=0;be<5;be++)if(ob.count({good,be}))
      cout<<" beta55="<<be<<" ordered="<<ob[{good,be}]<<" swap="<<sb[{good,be}]
          <<" unordered="<<(ob[{good,be}]+sb[{good,be}])/2<<"\n";
    for(int qt=0;qt<2;qt++)for(int be=0;be<5;be++)if(cb.count({qt,good,be}))
      cout<<" type="<<(qt?'B':'A')<<" beta45="<<be<<" orbits="<<cb[{qt,good,be}]<<"\n";
  }
  cout<<"THEOREM: after the universal signed filter, pencil-rigid orbit counts are "
      <<"4+5=4260 and 5+5=3810812\n";
}
