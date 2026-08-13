#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <mutex>
#include <numeric>
#include <queue>
#include <tuple>
#include <utility>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

using u16=uint16_t; using u64=uint64_t;
static constexpr u16 NONE=65535;
struct Mask { u64 lo,hi; };
struct Node { std::array<unsigned char,8> p; int parent,gen; };

static int perm_rank(const std::array<unsigned char,8>&p){
 int rank=0;
 for(int i=0;i<8;i++){
  int c=0;for(int j=i+1;j<8;j++)c+=p[j]<p[i];
  rank=rank*(8-i)+c;
 }
 return rank;
}

static u64 pair_index(u16 aa,u16 bb,u16 n){
 u64 a=aa,b=bb;if(a>b)std::swap(a,b);
 return a*(2ull*n-a-1)/2+(b-a-1);
}

int main(int argc,char**argv){
 if(argc!=3){
  std::cerr<<"usage: "<<argv[0]<<" INPUT OUTPUT\n";
  return 2;
 }
 std::ifstream in(argv[1],std::ios::binary);
 uint32_t n,npairs,ngen;in.read((char*)&n,4);in.read((char*)&npairs,4);in.read((char*)&ngen,4);
 if(n!=26740||npairs!=9476||ngen!=7){std::cerr<<"bad header\n";return 2;}
 std::vector<u16> gen((size_t)ngen*n);in.read((char*)gen.data(),gen.size()*2);
 std::vector<Mask> masks(n);in.read((char*)masks.data(),masks.size()*sizeof(Mask));
 std::vector<std::pair<u16,u16>> reps(npairs);in.read((char*)reps.data(),reps.size()*4);
 if(!in){std::cerr<<"short input\n";return 2;}

 // BFS of S8 by left adjacent transpositions.  A child q=s o p has
 // factor action T_q=T_s o T_p, so its action row is gen_s[parent_row].
 std::vector<Node> nodes;nodes.reserve(40320);
 std::array<int,40320> rank_to_node;rank_to_node.fill(-1);
 Node id{};for(int i=0;i<8;i++)id.p[i]=i;id.parent=-1;id.gen=-1;
 nodes.push_back(id);rank_to_node[perm_rank(id.p)]=0;
 for(size_t at=0;at<nodes.size();at++)for(int s=0;s<7;s++){
  Node q=nodes[at];q.parent=(int)at;q.gen=s;
  for(int i=0;i<8;i++){if(q.p[i]==s)q.p[i]=s+1;else if(q.p[i]==s+1)q.p[i]=s;}
  int r=perm_rank(q.p);if(rank_to_node[r]<0){rank_to_node[r]=nodes.size();nodes.push_back(q);}
 }
 if(nodes.size()!=40320){std::cerr<<"bad group "<<nodes.size()<<"\n";return 2;}
 std::vector<u16> inverse(nodes.size());
 for(size_t g=0;g<nodes.size();g++){
  std::array<unsigned char,8> q{};for(int i=0;i<8;i++)q[nodes[g].p[i]]=i;
  inverse[g]=rank_to_node[perm_rank(q)];
 }
 std::cerr<<"GROUP "<<nodes.size()<<"\n";

 size_t action_size=nodes.size()*(size_t)n;
 std::vector<u16> action(action_size);
 for(u16 f=0;f<n;f++)action[f]=f;
 for(size_t g=1;g<nodes.size();g++){
  const u16* pr=&action[(size_t)nodes[g].parent*n];u16* out=&action[g*(size_t)n];
  const u16* gg=&gen[(size_t)nodes[g].gen*n];
  for(u16 f=0;f<n;f++)out[f]=gg[pr[f]];
 }
 // Exact inverse-action canary.
 for(size_t g=0;g<nodes.size();g+=137)for(u16 f=0;f<n;f+=911){
  if(action[(size_t)inverse[g]*n+action[g*(size_t)n+f]]!=f){std::cerr<<"inverse fail\n";return 2;}
 }
 std::cerr<<"ACTION built entries="<<action_size<<"\n";

 const u64 labeled_pairs=(u64)n*(n-1)/2;
 std::vector<u16> pair_id(labeled_pairs,NONE),pair_align(labeled_pairs,NONE);
 std::vector<std::vector<u16>> stabilizer(npairs);
 #pragma omp parallel for schedule(dynamic,1)
 for(int pp=0;pp<(int)npairs;pp++){
  auto [a,b]=reps[pp];
  std::vector<u16> localstab;
  for(u16 g=0;g<40320;g++){
   u16 x=action[(size_t)g*n+a],y=action[(size_t)g*n+b];if(x>y)std::swap(x,y);
   u64 ix=pair_index(x,y,n);
   // Different pair orbits are disjoint, so only same-thread duplicate writes occur.
   pair_id[ix]=pp;pair_align[ix]=inverse[g];
   u16 aa=a,bb=b;if(aa>bb)std::swap(aa,bb);
   if(x==aa&&y==bb)localstab.push_back(g);
  }
  stabilizer[pp]=std::move(localstab);
 }
 u64 unfilled=0;for(u64 x=0;x<labeled_pairs;x++)unfilled+=pair_id[x]==NONE||pair_align[x]==NONE;
 if(unfilled){std::cerr<<"unfilled pairs "<<unfilled<<"\n";return 2;}
 u64 stab_sum=0;int stab_max=0;for(auto&s:stabilizer){stab_sum+=s.size();stab_max=std::max(stab_max,(int)s.size());}
 std::cerr<<"PAIR table="<<labeled_pairs<<" stabsum="<<stab_sum<<" max="<<stab_max<<"\n";

 auto reduce_third=[&](u16 pid,u16 f)->u16{
  u16 z=f;for(u16 h:stabilizer[pid])z=std::min(z,action[(size_t)h*n+f]);return z;
 };
 auto key_for=[&](u16 a,u16 b,u16 c)->std::pair<u16,u16>{
  u64 ix=pair_index(a,b,n);u16 pid=pair_id[ix],al=pair_align[ix];
  u16 z=action[(size_t)al*n+c];z=reduce_third(pid,z);return {pid,z};
 };
 auto affine_any_frame=[&](u16 a,u16 b,u16 c,int &tried)->bool{
  for(int g=0;g<40320;g++){
   u16 x=action[(size_t)g*n+a],y=action[(size_t)g*n+b],z=action[(size_t)g*n+c];
   tried=g+1;
   if((masks[x].lo&masks[y].lo&masks[z].lo)||(masks[x].hi&masks[y].hi&masks[z].hi))return true;
  }
  return false;
 };

 // Pin the four known canaries before the long scan.
 const std::array<std::array<u16,3>,4> hard={{{12985,16183,7196},{20355,5442,5949},{9667,16486,26315},{9758,24338,15810}}};
 for(auto t:hard){int tried=0;bool ok=affine_any_frame(t[0],t[1],t[2],tried);std::cerr<<"HARD "<<t[0]<<","<<t[1]<<","<<t[2]<<" good="<<ok<<" tried="<<tried<<"\n";
  if(ok||tried!=40320){std::cerr<<"hard-canary regression\n";return 3;}
 }

 unsigned long long triples=0,good=0,bad=0,standard=0,frames=0;
 int maxframes=0;std::mutex examples_mutex;std::vector<std::array<u16,3>> examples;
 std::vector<std::vector<u16>> bad_thirds(npairs);
 #pragma omp parallel for schedule(dynamic,1) reduction(+:triples,good,bad,standard,frames) reduction(max:maxframes)
 for(int pp=0;pp<(int)npairs;pp++){
  auto [a,b]=reps[pp];
  struct Frame { u16 g; Mask common; };
  std::vector<Frame> usable;usable.reserve(40320);
  for(int g=0;g<40320;g++){
   u16 x=action[(size_t)g*n+a],y=action[(size_t)g*n+b];
   Mask c{masks[x].lo&masks[y].lo,masks[x].hi&masks[y].hi};
   if(c.lo||c.hi)usable.push_back(Frame{(u16)g,c});
  }
  std::vector<u16> candidates;candidates.reserve(n);
  for(u16 f=0;f<n;f++){
   if(f==a||f==b||reduce_third(pp,f)!=f)continue;
   std::pair<u16,u16> current={(u16)pp,f};
   auto k1=key_for(a,f,b);if(k1<current)continue;
   auto k2=key_for(b,f,a);if(k2<current)continue;
   candidates.push_back(f);
  }
  triples+=candidates.size();
  if(!usable.empty()&&usable[0].g==0){
   for(u16 f:candidates)standard+=((masks[f].lo&usable[0].common.lo)||(masks[f].hi&usable[0].common.hi));
  }
  // Frame-major elimination: all surviving thirds read the same contiguous
  // action row.  This is much faster than a 2 GiB strided scan per hard triple.
  std::vector<u16> alive=std::move(candidates),next;next.reserve(alive.size());
  for(size_t fi=0;fi<usable.size()&&!alive.empty();fi++){
   const auto &fr=usable[fi];const u16* row=&action[(size_t)fr.g*n];next.clear();
   for(u16 f:alive){u16 z=row[f];
    if((masks[z].lo&fr.common.lo)||(masks[z].hi&fr.common.hi)){good++;frames+=fi+1;}
    else next.push_back(f);
   }
   alive.swap(next);
  }
  bad+=alive.size();frames+=(unsigned long long)alive.size()*usable.size();
  bad_thirds[pp]=alive;
  if(!alive.empty())maxframes=std::max(maxframes,(int)usable.size());
  if(!alive.empty()){
   std::lock_guard<std::mutex> lock(examples_mutex);
   for(u16 f:alive)if(examples.size()<20)examples.push_back({a,b,f});
  }
  if(pp%500==0){
   #pragma omp critical
   std::cerr<<"PROGRESS pair="<<pp<<" triples="<<triples<<" good="<<good<<" bad="<<bad<<"\n";
  }
 }
 std::cout<<"TRIPLES "<<triples<<" GOOD "<<good<<" BAD "<<bad<<" STANDARD "<<standard<<" FRAMES "<<frames<<" MAXFRAMES "<<maxframes<<"\n";
 for(auto t:examples)std::cout<<"BAD_EXAMPLE "<<t[0]<<" "<<t[1]<<" "<<t[2]<<"\n";
 {
  std::ofstream bout(argv[2],std::ios::binary);
  bout.write((const char*)&npairs,4);
  for(uint32_t pp=0;pp<npairs;pp++){
   uint32_t count=bad_thirds[pp].size();bout.write((const char*)&count,4);
   if(count)bout.write((const char*)bad_thirds[pp].data(),count*2);
  }
 }
 std::cout<<"WROTE "<<argv[2]<<"\n";
 if(triples!=79102449ull){std::cerr<<"wrong triple orbit count\n";return 3;}
 if(good!=74767375ull||bad!=4335074ull||standard!=65557134ull){std::cerr<<"wrong affine-three census\n";return 3;}
 return 0;
}
