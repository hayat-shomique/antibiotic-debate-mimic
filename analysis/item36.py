import json,collections
full=[json.loads(l) for l in open('runs/debate_20260818.jsonl') if l.strip()]
full=[r for r in full if r.get('kind')=='full']
N=len(full)
print('=== ITEM 3 ABANDONMENT ===')
print('DENOM kind==full runs =',N,'| quarantined =',sum(1 for r in full if r['quarantined']))
print('stored changed_A non-null =',sum(1 for r in full if r.get('changed_A') is not None),'| stored changed_B present =',sum(1 for r in full if 'changed_B' in r))
print('recompute-vs-stored mismatches: A',sum(1 for r in full if r.get('changed_A') is not None and r['changed_A']!=(r['round0_drug']!=r['final_A'])),
      'B',sum(1 for r in full if 'changed_B' in r and r['changed_B']!=(r['round0_drug']!=r['final_B'])))
P=lambda n,d:'%d/%d = %.1f%%'%(n,d,100.0*n/d)
for lab,sub in [('ALL',full),('A-first',[r for r in full if r['ordering']=='A-first']),('B-first',[r for r in full if r['ordering']=='B-first'])]:
    d=len(sub)
    a=sum(1 for r in sub if r['round0_drug']!=r['final_A']); b=sum(1 for r in sub if r['round0_drug']!=r['final_B'])
    e=sum(1 for r in sub if r['round0_drug']!=r['final_A'] or r['round0_drug']!=r['final_B'])
    bo=sum(1 for r in sub if r['round0_drug']!=r['final_A'] and r['round0_drug']!=r['final_B'])
    print(lab,'(n=%d)'%d,'| agentA',P(a,d),'| agentB',P(b,d),'| EITHER',P(e,d),'| BOTH',P(bo,d))
print('round0_drug dist:',dict(collections.Counter(r['round0_drug'] for r in full)))
print('final_A dist:',dict(collections.Counter(r['final_A'] for r in full)))
print()
print('=== ITEM 6 ORDER EFFECT ===')
by=collections.defaultdict(dict)
for r in full: by[r['case_id']][r['ordering']]=r
paired=sorted(c for c,d in by.items() if 'A-first' in d and 'B-first' in d)
Pn=len(paired)
print('cases in file =',len(by),'| cases with BOTH orderings (PAIRED DENOM) =',Pn)
for fld in ('final_A','final_B'):
    n=sum(1 for c in paired if by[c]['A-first'][fld]!=by[c]['B-first'][fld])
    print('order effect using %s: %d/%d = %.1f%%'%(fld,n,Pn,100.0*n/Pn))
amb=sorted({c for c in paired for o in ('A-first','B-first') if by[c][o]['final_A']!=by[c][o]['final_B']})
print('cases with intra-run A/B disagreement (run-final ambiguous):',amb)
unamb=[c for c in paired if c not in amb]
n=sum(1 for c in unamb if by[c]['A-first']['final_A']!=by[c]['B-first']['final_A'])
print('consensus definition on the %d unambiguous cases: %d/%d = %.1f%%'%(len(unamb),n,len(unamb),100.0*n/len(unamb)))
fin=set(r['final_A'] for r in full)|set(r['final_B'] for r in full)
allv=fin|set(r['round0_drug'] for r in full)|set(t['recommendation'] for r in full for t in r['tidy'])
print('distinct drugs in FINAL positions:',len(fin),sorted(fin))
print('distinct drugs anywhere (round0+turns+finals):',len(allv),sorted(allv))
print('formulary_size (model_registry.json):',json.load(open('model_registry.json'))['formulary_size'])
