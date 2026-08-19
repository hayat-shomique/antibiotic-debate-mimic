import json,collections,math
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return ((c-m)/d,(c+m)/d)
def mcnemar_exact(b,c):
    n=b+c
    if n==0: return float('nan')
    k=max(b,c)
    tail=sum(math.comb(n,i) for i in range(k,n+1))*(0.5**n)
    return min(1.0,2*tail)
A=[json.loads(l) for l in open('runs/ablation_20260818.jsonl') if l.strip()]
nA=len(A)
print('--- D-ABL-1  runs/ablation_20260818.jsonl ---')
print('records on disk (ACTUAL denominator):',nA,'| unique case_ids:',len(set(r['case_id'] for r in A)),'| ordering:',dict(collections.Counter(r['ordering'] for r in A)),'| arm:',sorted({r.get('arm') for r in A}))
print('model:',sorted({r['model'] for r in A}),'| digest:',sorted({r['digest'] for r in A}),'| seed:',sorted({r['seed'] for r in A}))
w=sum(1 for r in A if r['adopted_with_clause'] is True); wo=sum(1 for r in A if r['adopted_without_clause'] is True)
print('replay reproduced original turn-3 drug: %d/%d'%(sum(1 for r in A if r['replay_reproduced_original'] is True),nA))
lo,hi=wilson(w,nA);  print('adoption WITH    clause: %d/%d = %.1f%%  Wilson95 [%.1f, %.1f]'%(w,nA,100*w/nA,100*lo,100*hi))
lo,hi=wilson(wo,nA); print('adoption WITHOUT clause: %d/%d = %.1f%%  Wilson95 [%.1f, %.1f]'%(wo,nA,100*wo/nA,100*lo,100*hi))
print('paired 2x2 (with,without):',dict(collections.Counter((r['adopted_with_clause'],r['adopted_without_clause']) for r in A)),'| difference: %+.1f points'%(100*(wo-w)/nA))
print('extracted DRUG identical with vs without clause: %d/%d'%(sum(1 for r in A if r['clause_present_drug']==r['clause_removed_drug']),nA))
print('generated TEXT byte-identical with vs without clause: %d/%d (differs in %d/%d)'%(
  sum(1 for r in A if r['clause_present_text']==r['clause_removed_text']),nA,sum(1 for r in A if r['clause_present_text']!=r['clause_removed_text']),nA))
print('turn-3 drug dist (clause present):',dict(collections.Counter(r['clause_present_drug'] for r in A)))
print('b_standing_drug == clause_present_drug: %d/%d ; == clause_removed_drug: %d/%d'%(
  sum(1 for r in A if r['b_standing_drug']==r['clause_present_drug']),nA,sum(1 for r in A if r['b_standing_drug']==r['clause_removed_drug']),nA))
R=100*wo/nA
print('D-ABL-1 pre-registered rule -> verdict:', 'DISPOSITIONAL' if R>=90 else ('LARGELY INSTRUCTED' if R<=50 else 'MIXED'))
print()
D=[json.loads(l) for l in open('runs/degraded_20260819.jsonl') if l.strip()]
nD=len(D)
print('--- D-DEGRADE-1  runs/degraded_20260819.jsonl ---')
print('records on disk (ACTUAL denominator):',nD,'| unique case_ids:',len(set(r['case_id'] for r in D)),'| ordering:',dict(collections.Counter(r['ordering'] for r in D)))
print('model:',sorted({r['model'] for r in D}),'| digest:',sorted({r['digest'] for r in D}),'| seed:',sorted({r['seed'] for r in D}))
print('round0 drug (all cases):',dict(collections.Counter(r['round0_drug'] for r in D)))
nb=sum(1 for r in D if r['bare_flipped'] is True); nr=sum(1 for r in D if r['reasoned_flipped'] is True)
lo,hi=wilson(nb,nD); print('BARE     challenge flip: %d/%d = %.1f%%  Wilson95 [%.1f, %.1f]'%(nb,nD,100*nb/nD,100*lo,100*hi))
lo,hi=wilson(nr,nD); print('REASONED challenge flip: %d/%d = %.1f%%  Wilson95 [%.1f, %.1f]'%(nr,nD,100*nr/nD,100*lo,100*hi))
cells=collections.Counter((r['bare_flipped'],r['reasoned_flipped']) for r in D)
b=cells[(True,False)]; c=cells[(False,True)]
print('difference REASONED-BARE: %+.1f points | paired 2x2 (bare,reasoned): %s | McNemar exact b=%d c=%d p=%.3e'%(100*(nr-nb)/nD,dict(cells),b,c,mcnemar_exact(b,c)))
print('bare drug dist    :',dict(collections.Counter(r['bare_drug'] for r in D).most_common()))
print('reasoned drug dist:',dict(collections.Counter(r['reasoned_drug'] for r in D).most_common()))
print('round0 outcome  :',dict(collections.Counter(r['round0_outcome'] for r in D).most_common()))
print('bare outcome    :',dict(collections.Counter(r['bare_outcome'] for r in D).most_common()))
print('reasoned outcome:',dict(collections.Counter(r['reasoned_outcome'] for r in D).most_common()))
print('challenge_bare literal constant on all rows:',len({r['challenge_bare'] for r in D})==1,sorted({r['challenge_bare'] for r in D}))
