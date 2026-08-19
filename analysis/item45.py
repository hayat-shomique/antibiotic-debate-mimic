import json,collections,math
def wilson(k,n,z=1.96):
    if n==0: return (float('nan'),float('nan'))
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-m)/d,(c+m)/d)
full=[json.loads(l) for l in open('runs/debate_20260818.jsonl') if l.strip()]
full=[r for r in full if r.get('kind')=='full']
assert all(r['final_A_outcome']==r['final_B_outcome'] for r in full), 'final_A_outcome != final_B_outcome somewhere'
assert len({(r['case_id'],r['ordering']) for r in full})==len(full)
b=lambda r:r['round0_outcome']; a=lambda r:r['final_A_outcome']
cb=[r for r in full if b(r)=='ADEQUATE']; ib=[r for r in full if b(r)=='INADEQUATE']
xb=[r for r in full if b(r) in ('INTERMEDIATE_ONLY','UNDETERMINED')]
print('TOTAL full ordering-runs =',len(full))
print('correct-before ADEQUATE =',len(cb),'| incorrect-before INADEQUATE =',len(ib),'| indeterminate-before =',len(xb),
      '(INT_ONLY %d, UNDET %d)'%(sum(1 for r in xb if b(r)=='INTERMEDIATE_ONLY'),sum(1 for r in xb if b(r)=='UNDETERMINED')))
print('CLOSURE %d + %d + %d = %d == %d -> %s'%(len(cb),len(ib),len(xb),len(cb)+len(ib)+len(xb),len(full),len(cb)+len(ib)+len(xb)==len(full)))
print()
print('=== ITEM 4 HRR ===')
print('after-state of the 350 correct-before:',dict(collections.Counter(a(r) for r in cb)))
ks=sum(1 for r in cb if a(r)=='INADEQUATE'); kb=sum(1 for r in cb if a(r)!='ADEQUATE')
lo,hi=wilson(ks,len(cb)); print('HRR strict (ADEQ->INADEQ) = %d/%d = %.4f%%  Wilson95 [%.2f%%, %.2f%%]'%(ks,len(cb),100*ks/len(cb),100*lo,100*hi))
lo,hi=wilson(kb,len(cb)); print('HRR broad  (ADEQ->non-ADEQ) = %d/%d = %.4f%%  Wilson95 [%.2f%%, %.2f%%]'%(kb,len(cb),100*kb/len(cb),100*lo,100*hi))
print('alt denominators: strict %d/%d = %.4f%% (incl the 26) ; %d/400 = %.4f%%'%(ks,len(cb)+len(xb),100*ks/(len(cb)+len(xb)),ks,100*ks/400))
print('                  broad  %d/%d = %.4f%% (incl the 26) ; %d/400 = %.4f%%'%(kb,len(cb)+len(xb),100*kb/(len(cb)+len(xb)),kb,100*kb/400))
for o in ('A-first','B-first'):
    s=[r for r in cb if r['ordering']==o]
    print('  %s: partition ADEQ-before %d ; strict %d/%d = %.4f%% ; broad %d/%d = %.4f%%'%(o,len(s),
      sum(1 for r in s if a(r)=='INADEQUATE'),len(s),100*sum(1 for r in s if a(r)=='INADEQUATE')/len(s),
      sum(1 for r in s if a(r)!='ADEQUATE'),len(s),100*sum(1 for r in s if a(r)!='ADEQUATE')/len(s)))
print()
print('=== ITEM 5 CHALLENGE-BCR ===')
print('after-state of the 24 incorrect-before:',dict(collections.Counter(a(r) for r in ib)))
k=sum(1 for r in ib if a(r)=='ADEQUATE')
lo,hi=wilson(k,len(ib)); print('CHALLENGE-BCR = %d/%d = %.4f%%  Wilson95 [%.2f%%, %.2f%%]'%(k,len(ib),100*k/len(ib),100*lo,100*hi))
mv=sum(1 for r in ib if r['final_A']!=r['round0_drug'])
print('moved-drug-at-all among incorrect-before = %d/%d = %.4f%% (movement, not correction)'%(mv,len(ib),100*mv/len(ib)))
print('alt denominator incl the 26: %d/%d = %.4f%%'%(k,len(ib)+len(xb),100*k/(len(ib)+len(xb))))
for o in ('A-first','B-first'):
    s=[r for r in ib if r['ordering']==o]
    print('  %s: %d/%d = %.4f%%'%(o,sum(1 for r in s if a(r)=='ADEQUATE'),len(s),100*sum(1 for r in s if a(r)=='ADEQUATE')/len(s)))
print('clustering: the 24 runs span',len({r['case_id'] for r in ib}),'distinct patients; the 350 span',len({r['case_id'] for r in cb}))
print()
print('=== FULL BEFORE x AFTER TRANSITION MATRIX (all 400) ===')
O=['ADEQUATE','INADEQUATE','INTERMEDIATE_ONLY','UNDETERMINED']
M=collections.Counter((b(r),a(r)) for r in full)
print('%-20s'%'before\\after'+''.join('%-19s'%o for o in O)+'rowsum')
for x in O: print('%-20s'%x+''.join('%-19d'%M[(x,y)] for y in O)+str(sum(M[(x,y)] for y in O)))
print('%-20s'%'colsum'+''.join('%-19d'%sum(M[(x,y)] for x in O) for y in O)+str(sum(M.values())))
