import json, collections
P='/Users/shamzzzh/brain_run/runs/debate_20260818.jsonl'
r0=[json.loads(l) for l in open(P) if json.loads(l).get('kind')=='round0']
c=collections.Counter((d['case_id'],d['ordering']) for d in r0)
dup=[k for k,v in c.items() if v>1]
print('round0 lines =',len(r0),'unique units =',len(c),'duplicated units =',dup)
for k in dup:
    recs=[d for d in r0 if (d['case_id'],d['ordering'])==k]
    print('  identical payload?', recs[0]==recs[1], '| outcomes:', [r['outcome'] for r in recs], '| drugs:', [r['drug'] for r in recs])

full=[json.loads(l) for l in open(P)]; full=[r for r in full if r.get('kind')=='full']
before=lambda r:r['round0_outcome']; after=lambda r:r['final_A_outcome']
bypat=collections.defaultdict(list)
for r in full: bypat[r['case_id']].append(r)
print()
print('patients with both orderings:', sum(1 for v in bypat.values() if len(v)==2), '/', len(bypat))
print('patients whose two runs share the same before-state:', sum(1 for v in bypat.values() if len(set(before(r) for r in v))==1))
pb=collections.Counter(before(v[0]) for v in bypat.values())
print('patient-level before partition:', dict(pb), 'sum =', sum(pb.values()))
# patient-level harm: both runs harmful / one / none, among 175 adequate-before patients
adq=[v for v in bypat.values() if before(v[0])=='ADEQUATE']
h=collections.Counter(sum(1 for r in v if after(r)=='INADEQUATE') for v in adq)
print('among 175 correct-before patients, #runs that went INADEQUATE (0/1/2):', dict(h),
      '-> harmful runs =', sum(k*n for k,n in h.items()))
ina=[v for v in bypat.values() if before(v[0])=='INADEQUATE']
b=collections.Counter(sum(1 for r in v if after(r)=='ADEQUATE') for v in ina)
print('among 12 incorrect-before patients, #runs corrected (0/1/2):', dict(b),
      '-> corrected runs =', sum(k*n for k,n in b.items()))
