import json,csv,collections
O=['ADEQUATE','INADEQUATE','INTERMEDIATE_ONLY','UNDETERMINED']
def row(lbl,c):
    n=sum(c[o] for o in O); d1=c['ADEQUATE']+c['INADEQUATE']; d2=n-c['UNDETERMINED']
    f=lambda x,d:'undef' if not d else '%.1f%%'%(100*x/d)
    print('%-34s ALL n=%d  ADEQ=%d(%s) INADEQ=%d(%s) INT=%d(%s) UNDET=%d(%s) | D1 n=%d ADEQ=%s | D2 n=%d ADEQ=%s'%(
        lbl,n,c['ADEQUATE'],f(c['ADEQUATE'],n),c['INADEQUATE'],f(c['INADEQUATE'],n),c['INTERMEDIATE_ONLY'],f(c['INTERMEDIATE_ONLY'],n),
        c['UNDETERMINED'],f(c['UNDETERMINED'],n),d1,f(c['ADEQUATE'],d1),d2,f(c['ADEQUATE'],d2)))
rs=[r for r in csv.DictReader(open('floor_reconciled.csv')) if r['frame']=='C_sampled_200']
print('floor_reconciled.csv frame=C_sampled_200 agents=%d'%len(rs))
print('=== ALL 17 FLOOR AGENTS, frame C_sampled_200, n_cases=200 each ===')
for r in sorted(rs,key=lambda r:-int(r['n_adequate'])):
    row('FLOOR '+r['agent'],collections.Counter({'ADEQUATE':int(r['n_adequate']),'INADEQUATE':int(r['n_inadequate']),'INTERMEDIATE_ONLY':int(r['n_intermediate_only']),'UNDETERMINED':int(r['n_undetermined'])}))
j=json.load(open('clinician_comparator_v2_summary.json'))
print('=== CLINICIAN ===')
row('CLINICIAN clinician_primary',collections.Counter(j['clinician_primary']['counts']))
print('  json n_cases=%s n_determined=%s pct_of_determined=%s'%(j['clinician_primary']['n_cases'],j['clinician_primary']['n_determined'],j['clinician_primary']['pct_of_determined']))
cr=list(csv.DictReader(open('clinician_comparator_v2.csv')))
print('  clinician_comparator_v2.csv rows=%d clinician_outcome=%s floor_outcome=%s'%(len(cr),dict(collections.Counter(x['clinician_outcome'] for x in cr)),dict(collections.Counter(x['floor_outcome'] for x in cr))))
recs=[json.loads(l) for l in open('runs/debate_20260818.jsonl') if l.strip()]
r0=[d for d in recs if d['kind']=='round0']
seen={}
for d in r0: seen.setdefault((d['case_id'],d['ordering']),d)
byc=collections.defaultdict(dict)
for (c_,o),d in seen.items(): byc[c_][o]=d
print('=== MODEL ROUND-0 (runs/debate_20260818.jsonl kind==round0) ===')
print('raw round0 records=%d  uniq(case,ordering)=%d  uniq case_id=%d  dup keys=%s'%(len(r0),len(seen),len(byc),[k for k,v in collections.Counter((d['case_id'],d['ordering']) for d in r0).items() if v>1]))
print('round0 drug over the 400 deduped ordering-runs: %s'%dict(collections.Counter(d['drug'] for d in seen.values())))
print('round0 drug at case level (A-first): %s'%dict(collections.Counter(v['A-first']['drug'] for v in byc.values())))
row('MODEL ROUND-0 case level (n=200)',collections.Counter(v['A-first']['outcome'] for v in byc.values()))
row('MODEL ROUND-0 deduped runs (n=400)',collections.Counter(d['outcome'] for d in seen.values()))
row('MODEL ROUND-0 raw persisted (n=401)',collections.Counter(d['outcome'] for d in r0))
print('=== IS MODEL ROUND-0 THE CONSTANT PIP-TAZO FLOOR? ===')
pt=[r for r in rs if r['agent']=='piperacillin-tazobactam'][0]
print('floor pip-tazo C_sampled_200 counts: ADEQ=%s INADEQ=%s INT=%s UNDET=%s'%(pt['n_adequate'],pt['n_inadequate'],pt['n_intermediate_only'],pt['n_undetermined']))
mc=collections.Counter(v['A-first']['outcome'] for v in byc.values())
print('model round0 case-level counts:      ADEQ=%d INADEQ=%d INT=%d UNDET=%d'%(mc['ADEQUATE'],mc['INADEQUATE'],mc['INTERMEDIATE_ONLY'],mc['UNDETERMINED']))
print('aggregate identical: %s'%(mc['ADEQUATE']==int(pt['n_adequate']) and mc['INADEQUATE']==int(pt['n_inadequate']) and mc['INTERMEDIATE_ONLY']==int(pt['n_intermediate_only']) and mc['UNDETERMINED']==int(pt['n_undetermined'])))
better=[(r['agent'],r['pct_of_all']) for r in rs if float(r['pct_of_all'])>87.5]
print('floor agents strictly above model round-0 87.5%%: %s'%better)
