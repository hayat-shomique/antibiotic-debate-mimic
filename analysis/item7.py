import json,collections
rows=[json.loads(l) for l in open('runs/c0cn_20260818.jsonl') if l.strip()]
print('FILE=runs/c0cn_20260818.jsonl  ACTUAL PERSISTED RECORDS (denominator) =',len(rows))
print('unique case_id =',len(set(r['case_id'] for r in rows)),'| condition =',dict(collections.Counter(r['condition'] for r in rows)))
print('MOVED by stored flag changed_under_neutral==True : %d/%d'%(sum(1 for r in rows if r['changed_under_neutral']),len(rows)))
print('MOVED by recomputed c0_drug != cn_drug           : %d/%d'%(sum(1 for r in rows if r['c0_drug']!=r['cn_drug']),len(rows)))
print('MOVED by recomputed c0_outcome != cn_outcome     : %d/%d'%(sum(1 for r in rows if r['c0_outcome']!=r['cn_outcome']),len(rows)))
print('stored flag agrees with recomputed drug-change on all rows:',all(r['changed_under_neutral']==(r['c0_drug']!=r['cn_drug']) for r in rows))
print('c0_outcome dist:',dict(collections.Counter(r['c0_outcome'] for r in rows)))
print('cn_outcome dist:',dict(collections.Counter(r['cn_outcome'] for r in rows)))
print('C0->Cn crosstab:',dict(collections.Counter((r['c0_outcome'],r['cn_outcome']) for r in rows)))
print('c0_drug dist:',dict(collections.Counter(r['c0_drug'] for r in rows)),'| cn_drug dist:',dict(collections.Counter(r['cn_drug'] for r in rows)))
print('reason-text differs while drug+outcome identical: %d/%d'%(sum(1 for r in rows if r['c0_text']!=r['cn_text']),len(rows)))
print('determinism_match==False: %d/%d'%(sum(1 for r in rows if not r['determinism_match']),len(rows)))
