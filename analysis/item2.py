import json,collections
O=['ADEQUATE','INADEQUATE','INTERMEDIATE_ONLY','UNDETERMINED']
f=[json.loads(l) for l in open('runs/debate_20260818.jsonl') if l.strip()]
f=[d for d in f if d['kind']=='full']
print('kind==full persisted=%d uniq(case,ordering)=%d uniq case_id=%d quarantined=%d nullfinal=%d'%(
  len(f),len(set((d['case_id'],d['ordering']) for d in f)),len(set(d['case_id'] for d in f)),
  sum(1 for d in f if d.get('quarantined')),sum(1 for d in f if not d.get('final_A') or not d.get('final_B'))))
def row(lbl,c):
    n=sum(c[o] for o in O); d1=c['ADEQUATE']+c['INADEQUATE']; d2=n-c['UNDETERMINED']
    p=lambda x,d:'undef' if not d else '%.1f%%'%(100*x/d)
    print('%-30s ALL n=%d ADEQ=%d(%s) INADEQ=%d(%s) INT=%d(%s) UNDET=%d(%s) | D1 n=%d ADEQ=%s | D2 n=%d ADEQ=%s'%(
      lbl,n,c['ADEQUATE'],p(c['ADEQUATE'],n),c['INADEQUATE'],p(c['INADEQUATE'],n),c['INTERMEDIATE_ONLY'],p(c['INTERMEDIATE_ONLY'],n),c['UNDETERMINED'],p(c['UNDETERMINED'],n),d1,p(c['ADEQUATE'],d1),d2,p(c['ADEQUATE'],d2)))
row('AGENT A all 400 runs',collections.Counter(d['final_A_outcome'] for d in f))
row('AGENT B all 400 runs',collections.Counter(d['final_B_outcome'] for d in f))
for o in ['A-first','B-first']:
    s=[d for d in f if d['ordering']==o]
    row('AGENT A %s n=%d'%(o,len(s)),collections.Counter(d['final_A_outcome'] for d in s))
    row('AGENT B %s n=%d'%(o,len(s)),collections.Counter(d['final_B_outcome'] for d in s))
sd=sum(1 for d in f if d['final_A']==d['final_B']); so=sum(1 for d in f if d['final_A_outcome']==d['final_B_outcome'])
print('COLLAPSE drug-identical %d/%d = %.2f%% | outcome-identical %d/%d = %.2f%% | agreement==True %d | agreement==drug-equality on all records: %s'%(
  sd,len(f),100*sd/len(f),so,len(f),100*so/len(f),sum(1 for d in f if d['agreement'] is True),all((d['agreement'] is True)==(d['final_A']==d['final_B']) for d in f)))
print('joint outcome cross-tab:',dict(collections.Counter((d['final_A_outcome'],d['final_B_outcome']) for d in f)))
for d in f:
    if d['final_A']!=d['final_B']: print('DISSENT: case=%s ordering=%s final_A=%s(%s) final_B=%s(%s) round0_drug=%s'%(d['case_id'],d['ordering'],d['final_A'],d['final_A_outcome'],d['final_B'],d['final_B_outcome'],d['round0_drug']))
print('final_A drugs:',collections.Counter(d['final_A'] for d in f).most_common())
print('final_B drugs:',collections.Counter(d['final_B'] for d in f).most_common())
