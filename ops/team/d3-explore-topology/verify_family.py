#!/usr/bin/env python3
"""Exact replay of one complete horizontal badness chord and its vertical escape.
Standard library only. This is a producer replay; independent acceptance is separate.
"""
import ast,struct,zipfile,json,time,resource
from fractions import Fraction as Q
from math import comb,gcd
from hashlib import sha256
from itertools import combinations
import exact_chord as m
OWN=m.OWN;ROOT=m.ROOT
L=Q(-57869127,931628);H=Q(1094609,751872)
ALO=Q(-11894526,1000000);AHI=Q(-11894525,1000000)
BETA=Q(25705570474457532120686053,90789965179380319561365368)
VHIGH=Q(2037283091,10548542)
P1=[Q(57534309,313078783),Q(-457847691,820936147),Q(-1),Q(29211737,391355821)]
BADSUPPORTS=[[9,19,21,37,38],[9,16,27,30,35],[11,16,17,24,40]]
VERTSUPPORTS=[[19,20,21,37,38],BADSUPPORTS[1],BADSUPPORTS[2]]
def require(c,msg):
 if not c:raise AssertionError(msg)
def dot(a,b):
 z=[Q(0)]
 for x,y in zip(a,b):z=m.add(z,m.mul(x,y))
 return z
def bern(p,l,h):
 n=len(p)-1;c=[sum(p[k]*comb(k,j)*l**(k-j)*(h-l)**j for k in range(j,n+1)) for j in range(n+1)]
 return [sum(c[j]*Q(comb(k,j),comb(n,j)) for j in range(k+1)) for k in range(n+1)]
def positive(p,l,h):require(min(bern(p,l,h))>0,'strict positive polynomial')
def constantdet(a):return m.det([[[Q(x)] for x in r] for r in a])[0]
def values_normals(parent):
 return [[(-1)**(r+3)*constantdet([[parent[k][j] for j in t] for k in range(4) if k!=r]) for r in range(4)] for t in m.TRIPLES]
def bracketvals(parent):return [constantdet([[parent[r][j] for j in b] for r in range(4)]) for b in m.BASES]
def npy(z,name):
 b=z.read(name+'.npy');require(b[:6]==b'\x93NUMPY','NPY magic');off=10 if b[6]==1 else 12
 hsize=struct.unpack('<H' if off==10 else '<I',b[8:off])[0];h=ast.literal_eval(b[off:off+hsize].decode());require(not h['fortran_order'],'NPY order')
 code={'<i8':'q','<u2':'H'}[h['descr']];raw=b[off+hsize:];return h['shape'],struct.unpack('<'+code*(len(raw)//struct.calcsize(code)),raw)
def admission():
 path='ai/omreal/data/seeat_parent2599_upper178.npz'
 with zipfile.ZipFile(ROOT/path) as z:
  shape,matrices=npy(z,'chart_matrix');_,assign=npy(z,'assignment');_,points=npy(z,'point')
 require(shape==(178,4,8),'bank shape')
 def chart(i):return [list(matrices[32*i+8*r:32*i+8*r+8]) for r in range(4)]
 require(chart(0)==m.P,'original bank chart');bv=bracketvals(m.P);sg=[1 if x>0 else -1 for x in bv]
 require(all(bv) and sg==m.src['parent_signs'],'source parent signs')
 records=json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json').read_text())['records'];noninclusions=0
 for i,a in enumerate(records):
  require(a['signature']==m.SIGS[i] and a['parent']==chart(a['upper_chart_index']),'proper anchor identity')
  require(assign[a['upper_point_index']]==a['upper_chart_index'] and a['point']==list(points[4*a['upper_point_index']:4*a['upper_point_index']+4]),'anchor bank point')
  require([1 if x>0 else -1 if x<0 else 0 for x in bracketvals(a['parent'])]==sg,'anchor parent signs')
  ns=values_normals(a['parent']);ns=[[x/gcd(*(int(y) for y in row)) for x in row] for row in ns]
  require(all((1 if m.SIGS[i]>>j&1 else -1)*sum(x*y for x,y in zip(row,a['point']))>0 for j,row in enumerate(ns)),'proper all-normal primal')
  for j,d in enumerate(a['other_systems']):
   require(d['signature']==m.SIGS[j],'other label')
   if j==i:continue
   sp=d['dual']['support'];ws=list(map(Q,d['dual']['weights']));require(all(x>0 for x in ws),'anchor dual positive')
   require(all(sum(w*(1 if m.SIGS[j]>>k&1 else -1)*ns[k][r] for k,w in zip(sp,ws))==0 for r in range(4)),'anchor dual equality');noninclusions+=1
 # Uniform rank-four GP signs on the full parent-plus-extension label set.
 ps=dict(zip(m.BASES,sg));ti={t:i for i,t in enumerate(m.TRIPLES)};gpchecks=0
 for sig in m.SIGS:
  def chi(seq):
   b=tuple(sorted(seq));v=(1 if sig>>ti[b[:3]]&1 else -1) if b[-1]==8 else ps[b]
   return (-1)**sum(seq[i]>seq[j] for i in range(4) for j in range(i+1,4))*v
  for lam in combinations(range(9),2):
   for a,b,c,d in combinations([i for i in range(9) if i not in lam],4):
    vals=[chi(lam+(a,b))*chi(lam+(c,d)),-chi(lam+(a,c))*chi(lam+(b,d)),chi(lam+(a,d))*chi(lam+(b,c))]
    require(len(set(vals))==2,'extension GP');gpchecks+=1
 require(noninclusions==6 and gpchecks==3780,'admission denominators')
 return {'bank_chart':0,'anchor_charts':[a['upper_chart_index'] for a in records],'ordered_noninclusions':noninclusions,'gp_relations':gpchecks}
def parent_interval(axis):
 b0=bracketvals(m.P);p=[r[:] for r in m.P];p[axis][7]+=1;b1=bracketvals(p)
 signed=[(abs(a),(b-a)*(1 if a>0 else -1)) for a,b in zip(b0,b1)]
 low=max(-c/d for c,d in signed if d>0);high=min(-c/d for c,d in signed if d<0)
 return low,high,signed

def main():
 start=time.monotonic();cpu=time.process_time();pins=json.loads((OWN/'SOURCE_MANIFEST.json').read_text())['source_sha256']
 for p,h in pins.items():require(sha256((ROOT/p).read_bytes()).hexdigest()==h,'source hash '+p)
 admitted=admission();lo,hi,walls=parent_interval(0);require((lo,hi)==(L,H),'maximal horizontal interval')
 ns=m.normals(0);a=m.signed(ns,m.SIGS[0],[19,21,37,38]);q=m.det(a)
 primitive=[int(x)//gcd(*(int(y) for y in q)) for x in q]
 require(primitive==[-37864449186859942661765893,-3195199993385149386840451,-996183819917173743324],'boundary polynomial')
 require(m.val(q,ALO)>0 and m.val(q,AHI)<0,'alpha isolated')
 # q is strictly decreasing throughout [L,H], so exactly one root alpha.
 positive(m.neg([q[1],2*q[2]]),L,H);require(L<ALO<AHI<0<BETA<H,'strict endpoint order')
 # Full all-56 strict primal on (L,alpha). Four basis inequalities equal q;
 # all other inequalities are strictly positive on the enclosing rational box.
 primal0=[m.det([[([Q(1)] if k==j else row[k]) for k in range(4)] for row in a]) for j in range(4)]
 for i,row in enumerate(m.signed(ns,m.SIGS[0],range(56))):
  p=dot(row,primal0)
  if i in [19,21,37,38]:require(p==q,'Cramer basis equality')
  else:positive(p,L,AHI)
 # Bad block 0 on [alpha,H): negative cofactor q becomes nonnegative;
 # every other weight stays strictly positive.
 duals=[]
 for i,sp in enumerate(BADSUPPORTS):
  rows=m.signed(ns,m.SIGS[i],sp);cs=m.cofactors(rows);sg=-1 if i==0 else 1;cs=[m.scale(p,sg) for p in cs]
  require(all(dot([r[j] for r in rows],cs)==[Q(0)] for j in range(4)),'identical Gordan kernel')
  if i==0:
   require(cs[0]==m.neg(q),'alpha weight')
   for p in cs[1:]:positive(p,ALO,H)
  elif i==1:
   require(m.val(cs[1],BETA)==0 and len(cs[1])==2 and cs[1][1]<0,'beta weight')
   for j,p in enumerate(cs):
    if j!=1:positive(p,L,BETA)
  else:
   for p in cs:positive(p,L,H)
  duals.append([m.dump(p) for p in cs])
 # Full all-56 strict primal on (beta,H). Use z=(u-beta)/(H-beta).
 rows=m.signed(ns,m.SIGS[1],[9,27,30]);p0=[m.val(m.scale(m.det([[row[k] for k in range(4) if k!=j] for row in rows]),(-1)**j),BETA) for j in range(4)]
 p0=[x/max(map(abs,p0)) for x in p0]
 if p0[2]>0:p0=[-x for x in p0]
 primal1=[[x,y-x] for x,y in zip(p0,P1)]
 for row in m.signed(ns,m.SIGS[1],range(56)):
  transformed=[[m.val(p,BETA),(p[1] if len(p)>1 else Q(0))*(H-BETA)] for p in row];p=dot(transformed,primal1);bc=bern(p,Q(0),Q(1))
  require(min(bc)>=0 and max(bc)>0,'right strict interior primal Bernstein')
 # Exact transverse escape of the entire horizontal interval's component.
 vl,vh,vwalls=parent_interval(1);require(vh==VHIGH and vl<0,'transverse parent endpoint')
 vn=m.normals(1);vduals=[]
 for sig,sp in zip(m.SIGS,VERTSUPPORTS):
  rows=m.signed(vn,sig,sp);cs=m.cofactors(rows)
  for p in cs:positive(p,Q(0),VHIGH)
  require(all(dot([r[j] for r in rows],cs)==[Q(0)] for j in range(4)),'vertical identical Gordan kernel')
  vduals.append([m.dump(p) for p in cs])
 zero=[i for i,(c,d) in enumerate(vwalls) if c+d*VHIGH==0];require(zero,'genuine parent boundary')
 require(all(c>0 and c+d*VHIGH>=0 for c,d in vwalls),'whole vertical parent segment')
 # The balanced bracket ratio is invariant under GL(4) and all eight
 # independent column scalings. It tends to zero with a nonzero denominator,
 # so this endpoint cannot be removed by a chart or projective gauge change.
 ep=[r[:] for r in m.P];ep[1][7]+=VHIGH
 eb=bracketvals(ep);bylabel={tuple(x+1 for x in b):v for b,v in zip(m.BASES,eb)}
 require(bylabel[(3,5,7,8)]==0 and bylabel[(1,2,3,8)]==Q(43095889251278677,10548542),'invariant limit values')
 require(bylabel[(1,2,3,4)]==2443943962 and bylabel[(3,4,5,7)]==4595799854,'fixed invariant factors')
 # Targeted hostile arithmetic and scope controls.
 controls={}
 def rejects(name,fn):
  try:fn()
  except AssertionError:controls[name]=True
  else:raise AssertionError('canary failed '+name)
 rejects('shifted_beta',lambda:require(m.val([Q(x) for x in duals[1][1]],BETA+Q(1,10**6))==0,'wrong beta'))
 rejects('negative_vertical_weight',lambda:positive(m.neg(m.cofactors(m.signed(vn,m.SIGS[0],VERTSUPPORTS[0]))[0]),Q(0),VHIGH))
 rejects('false_interior_infinity',lambda:require(any(c==0 for c,d in vwalls),'origin is not infinity'))
 changed=[r[:] for r in primal1];changed[0][0]+=1
 rejects('corrupted_primal',lambda:require(all(min(bern(dot([[m.val(p,BETA),(p[1] if len(p)>1 else Q(0))*(H-BETA)] for p in row],changed),Q(0),Q(1)))>=0 for row in m.signed(ns,m.SIGS[1],range(56))),'corrupt primal'))
 result={'classification':'FINITE_EXACT_COMPLETE_TWO_CHORD_FAMILY','ledger':'2/9','theorem_credit':0,'admission':admitted,'signatures':m.SIGS,'horizontal':{'parent_interval':[str(L),str(H)],'alpha_polynomial_ascending':[-x for x in primitive],'alpha_isolator':[str(ALO),str(AHI)],'beta':str(BETA),'states':'GBB on (L,alpha); BBB on [alpha,beta]; BGB on (beta,H)','dual_supports_zero_based':BADSUPPORTS,'dual_polynomials':duals,'left_primal_polynomials':list(map(m.dump,primal0)),'right_primal_in_z':list(map(m.dump,primal1))},'vertical':{'u':'0','v_interval':['0',str(VHIGH)],'strict_parent_until_final_endpoint':True,'all_three_bad_through_closed_interval':True,'boundary_bracket_labels':[[x+1 for x in m.BASES[i]] for i in zero],'dual_supports_zero_based':VERTSUPPORTS,'dual_polynomials':vduals},'conclusions':['The complete horizontal actual triple-bad slice is a compact interval strictly inside its parent chord.','That whole interval lies in one actual triple-bad component admitting the certified transverse escape to a nonuniform parent boundary.'],'nonconsequences':['No compact ambient triple-bad component is found.','No ambient component census, pair cohomology, global triple Hc0 vanishing, source residual reduction, or D3 theorem follows.'],'hostile_controls':controls,'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
 (OWN/'EXACT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['horizontal','vertical']},indent=2));print('boundary_brackets',result['vertical']['boundary_bracket_labels'])
if __name__=='__main__':main()
