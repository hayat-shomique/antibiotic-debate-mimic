import json,collections
def load(p): return [json.loads(l) for l in open(p) if l.strip()]
def ct(rows,anteF,postF,label,keyname):
    print('  antecedent (%s) dist: %s'%(anteF,dict(collections.Counter(r[anteF] for r in rows))))
    print('  CROSSTAB antecedent -> %s:'%postF)
    for (a,b),c in sorted(collections.Counter((r[anteF],r[postF]) for r in rows).items()):
        print('     %-18s -> %-18s : %d'%(a,b,c))
    for ante in ('INADEQUATE','ADEQUATE','INTERMEDIATE_ONLY','UNDETERMINED'):
        sub=[r for r in rows if r[anteF]==ante]
        if not sub: continue
        d=dict(collections.Counter(r[postF] for r in sub))
        pct={k:'%d/%d=%.1f%%'%(v,len(sub),100*v/len(sub)) for k,v in d.items()}
        print('     ENTERED %-18s n=%-4d -> %s'%(ante,len(sub),pct))

print('===== ITEM 8(a) REVEAL (post-debate C2) =====')
base=load('runs/reveal_20260818.jsonl')
print('BASE runs/reveal_20260818.jsonl rows=%d uniq case_id=%d uniq(case,ordering)=%d ordering=%s'%(
  len(base),len(set(r['case_id'] for r in base)),len({(r['case_id'],r['ordering']) for r in base}),dict(collections.Counter(r['ordering'] for r in base))))
ct(base,'final_A_outcome','reveal_outcome','base','k')
print()
rec=load('analysis/reveal_recovered_SNAPSHOT.jsonl')
print('RECOVERY SNAPSHOT (frozen copy of runs/reveal_recovered_20260819.jsonl taken 2026-08-19 17:59:48)')
print('  rows=%d uniq(case,ordering)=%d uniq case_id=%d kind=%s recovered_from_gate_defect=%s span_quarantine_true=%d'%(
  len(rec),len({(r['case_id'],r['ordering']) for r in rec}),len(set(r['case_id'] for r in rec)),
  dict(collections.Counter(r['kind'] for r in rec)),dict(collections.Counter(r['recovered_from_gate_defect'] for r in rec)),
  sum(1 for r in rec if r['span_quarantine'])))
print('  model=%s digest=%s seed=%s'%(sorted({r['model'] for r in rec}),sorted({r['digest'] for r in rec}),sorted({r['seed'] for r in rec})))
bk={(r['case_id'],r['ordering']) for r in base}; rk={(r['case_id'],r['ordering']) for r in rec}
print('  key overlap base vs recovered = %d'%len(bk&rk))
pool={}
for r in base: pool.setdefault((r['case_id'],r['ordering']),r)
for r in rec: pool.setdefault((r['case_id'],r['ordering']),r)
pl=list(pool.values())
print('POOLED DEDUPED SNAPSHOT rows=%d uniq case_id=%d ordering=%s'%(len(pl),len(set(r['case_id'] for r in pl)),dict(collections.Counter(r['ordering'] for r in pl))))
ct(pl,'final_A_outcome','reveal_outcome','pooled','k')
print()
print('===== ITEM 8(b) CLEAN-CONTEXT C2 =====')
b2=load('runs/cleanc2_20260819.jsonl'); r2=load('runs/cleanc2_recovered_20260819.jsonl')
print('BASE runs/cleanc2_20260819.jsonl rows=%d uniq case_id=%d arm=%s'%(len(b2),len(set(r['case_id'] for r in b2)),dict(collections.Counter(r['arm'] for r in b2))))
print('RECOVERY runs/cleanc2_recovered_20260819.jsonl rows=%d uniq case_id=%d kind=%s arm=%s span_quarantine_true=%d'%(
  len(r2),len(set(r['case_id'] for r in r2)),dict(collections.Counter(r['kind'] for r in r2)),dict(collections.Counter(r['arm'] for r in r2)),sum(1 for r in r2 if r['span_quarantine'])))
print('  recovery duplicate rows: %d rows for %d unique case_id'%(len(r2),len(set(r['case_id'] for r in r2))))
print('  model=%s digest=%s seed=%s'%(sorted({r['model'] for r in r2}),sorted({r['digest'] for r in r2}),sorted({r['seed'] for r in r2})))
print('  case_id overlap base vs recovered = %d'%len(set(r['case_id'] for r in b2)&set(r['case_id'] for r in r2)))
p2={}
for r in b2: p2.setdefault(r['case_id'],r)
for r in r2: p2.setdefault(r['case_id'],r)
pl2=list(p2.values())
print('POOLED DEDUPED rows=%d uniq case_id=%d'%(len(pl2),len(set(r['case_id'] for r in pl2))))
print('--- BASE ONLY (157) ---'); ct(b2,'round0_outcome','c2_outcome','base','k')
print('--- POOLED (200) ---'); ct(pl2,'round0_outcome','c2_outcome','pooled','k')
print('sanity: pooled clean-C2 round0_outcome dist vs c0cn C0 dist')
c0=[json.loads(l) for l in open('runs/c0cn_20260818.jsonl') if l.strip()]
print('  pooled cleanC2 round0_outcome:',dict(collections.Counter(r['round0_outcome'] for r in pl2)))
print('  c0cn c0_outcome            :',dict(collections.Counter(r['c0_outcome'] for r in c0)))
