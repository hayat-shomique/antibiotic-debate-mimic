import json, collections, sys
sys.path.insert(0,'/Users/shamzzzh/brain_run')
import brain_scoring_local as BS
P='/Users/shamzzzh/brain_run/runs/debate_20260818.jsonl'
full=[json.loads(l) for l in open(P)]
full=[r for r in full if r.get('kind')=='full']
before=lambda r: r['round0_outcome']; after=lambda r: r['final_A_outcome']

# keyset cohorts
ks=collections.Counter('has_round0_agent' if 'round0_agent' in r else 'NO_round0_agent' for r in full)
print('keyset cohorts among 400 full:', dict(ks))
sub=[r for r in full if 'round0_agent' not in r]
print('  the 16 without round0_agent -> before-state:', dict(collections.Counter(before(r) for r in sub)))
print('  the 16 without round0_agent -> orderings:', dict(collections.Counter(r['ordering'] for r in sub)))

# cross-check round0 kind records against full round0_outcome
r0={}
for l in open(P):
    d=json.loads(l)
    if d.get('kind')=='round0': r0[(d['case_id'],d['ordering'])]=d['outcome']
mism=[(r['case_id'],r['ordering'],before(r),r0.get((r['case_id'],r['ordering']))) for r in full
      if r0.get((r['case_id'],r['ordering'])) != before(r)]
print('round0-kind records:', len(r0), 'unique units; mismatches vs full.round0_outcome:', len(mism))
print('round0-kind outcome dist:', dict(collections.Counter(r0.values())))

# Wilson CIs
def ci(k,n): 
    lo,hi=BS.wilson_ci(k,n); return '[%.4f, %.4f] (%.2f%%, %.2f%%)'%(lo,hi,100*lo,100*hi)
print()
print('HRR strict 52/350 Wilson95:', ci(52,350))
print('HRR broad  61/350 Wilson95:', ci(61,350))
print('BCR        13/24  Wilson95:', ci(13,24))
print()
# per-ordering
for o in ('A-first','B-first'):
    s=[r for r in full if r['ordering']==o]
    cb=[r for r in s if before(r)=='ADEQUATE']; ib=[r for r in s if before(r)=='INADEQUATE']
    xb=[r for r in s if before(r) in ('INTERMEDIATE_ONLY','UNDETERMINED')]
    ks_=sum(1 for r in cb if after(r)=='INADEQUATE'); kb_=sum(1 for r in cb if after(r)!='ADEQUATE')
    kbcr=sum(1 for r in ib if after(r)=='ADEQUATE')
    print('%s: N=%d  partition %d+%d+%d=%d  HRRstrict=%d/%d=%.4f%%  HRRbroad=%d/%d=%.4f%%  BCR=%d/%d=%.4f%%'
      %(o,len(s),len(cb),len(ib),len(xb),len(cb)+len(ib)+len(xb),ks_,len(cb),100*ks_/len(cb),
        kb_,len(cb),100*kb_/len(cb),kbcr,len(ib),100*kbcr/len(ib) if ib else float('nan')))
print()
print('n patients (case_id) = %d ; runs = %d ; runs per patient = %.1f'
      %(len(set(r['case_id'] for r in full)), len(full), len(full)/len(set(r['case_id'] for r in full))))
cb=[r for r in full if before(r)=='ADEQUATE']; ib=[r for r in full if before(r)=='INADEQUATE']
print('correct-before spans %d distinct patients; incorrect-before spans %d distinct patients'
      %(len(set(r['case_id'] for r in cb)), len(set(r['case_id'] for r in ib))))
