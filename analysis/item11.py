import pathlib,datetime,json,collections
R=pathlib.Path('/Users/shamzzzh/brain_run')
def m(p):
    q=R/p
    return q.stat().st_mtime if q.exists() else None
def f(t): return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S') if t else 'MISSING'
def sz(p):
    q=R/p; return q.stat().st_size if q.exists() else None
DEB=m('runs/debate_20260818.jsonl')
FIG={
 'F1':('figures/src/f01_cohort_flow.py','figures/f1_cohort_flow',['cohort_gates_skeleton.csv','cohort_justification.md','inputs/cohort_skeleton.parquet','deviation_log.csv','deviation_log_tonight.csv','protocol/protocol_v1.md']),
 'F2':('figures/src/f02_gram_coverage.py','figures/f2_gram_coverage',['inputs/panel_rows.parquet','inputs/cohort_skeleton.parquet']),
 'F3':('figures/src/f03_floor_denominators.py','figures/f3_floor_denominators',['floor_reconciled.csv']),
 'F4':('figures/src/f04_fixed_policy.py','figures/f4_fixed_policy',['runs/model_compare_20260818.jsonl','runs/debate_20260818.jsonl','encoder_baseline.csv','model_registry.json','model_compare.py']),
 'F5':('figures/src/f05_core_endpoint.py','figures/f5_core_endpoint',['runs/debate_20260818.jsonl','runs/c0cn_20260818.jsonl','runs/reveal_20260818.jsonl','protocol/tingting_endpoint_spec.md']),
 'F6':('figures/src/f06_pattern_collapse.py','figures/f6_pattern_collapse',['runs/debate_20260818.jsonl']),
 'F7':('figures/src/f07_speaking_order.py','figures/f7_speaking_order',['runs/debate_20260818.jsonl','chain_topup.log']),
 'F8':('figures/src/f08_transition_matrix.py','figures/f8_transition_matrix',['runs/debate_20260818.jsonl']),
}
print('REFERENCE runs/debate_20260818.jsonl mtime=%s size=%d'%(f(DEB),sz('runs/debate_20260818.jsonl')))
print()
print('%-4s %-19s %-9s %-19s %-9s %-9s %-9s %s'%('ID','PNG mtime','PNG bytes','SVG mtime','SVG bytes','vs debate','vs inputs','newest declared input'))
nfresh=nstale=0
for k,(src,stem,ins) in FIG.items():
    png=m(stem+'.png'); svg=m(stem+'.svg')
    pres=[(i,m(i)) for i in ins]
    missing=[i for i,t in pres if t is None]
    newest=max([t for i,t in pres if t],default=None)
    newest_name=[i for i,t in pres if t==newest][0] if newest else 'none'
    vd='AFTER' if png>DEB else 'BEFORE'
    vi='REFRESHED' if (newest is None or png>newest) else 'STALE'
    if vi=='REFRESHED': nfresh+=1
    else: nstale+=1
    print('%-4s %-19s %-9d %-19s %-9d %-9s %-9s %s (%s)%s'%(k,f(png),sz(stem+'.png'),f(svg),sz(stem+'.svg'),vd,vi,newest_name,f(newest),' MISSING_INPUTS='+str(missing) if missing else ''))
print()
print('REFRESHED vs own declared inputs: %d/8 | STALE vs own declared inputs: %d/8'%(nfresh,nstale))
print('ALL 8 PNGs postdate runs/debate_20260818.jsonl: %s'%all(m(v[1]+'.png')>DEB for v in FIG.values()))
print('assets present: %d PNG + %d SVG (incl F0 swatch, not in the 8)'%(len(list((R/'figures').glob('*.png'))),len(list((R/'figures').glob('*.svg')))))
print()
print('=== FILES ON DISK NEWER THAN THE FIGURE BUILD (16:03:41) THAT NO F1-F8 SCRIPT REFERENCES ===')
build=max(m(v[1]+'.png') for v in FIG.values())
declared={i for v in FIG.values() for i in v[2]}
import glob as g
for p in sorted(g.glob(str(R/'runs'/'*.jsonl'))+g.glob(str(R/'protocol'/'*.md'))):
    rel=str(pathlib.Path(p).relative_to(R)); t=m(rel)
    if t and t>build:
        print('  %-45s mtime=%s  referenced_by_a_figure_script=%s'%(rel,f(t),rel in declared))
print()
print('=== F4 / F5 DRAFT CONDITIONS ===')
print('f04 hardcodes:',[l.strip() for l in open(R/'figures/src/f04_fixed_policy.py') if 'MODEL_COMPARE' in l and '=' in l][:1])
print('f04 uses glob:', 'glob' in open(R/'figures/src/f04_fixed_policy.py').read())
print('f05 SPEC line:',[l.strip() for l in open(R/'figures/src/f05_core_endpoint.py') if 'SPEC =' in l][:1])
print('protocol/tingting_endpoint_spec.md exists=%s size=%d mtime=%s ; f5 png mtime=%s ; gap=%.0f s'%(
  (R/'protocol/tingting_endpoint_spec.md').exists(),sz('protocol/tingting_endpoint_spec.md'),f(m('protocol/tingting_endpoint_spec.md')),f(m('figures/f5_core_endpoint.png')),m('protocol/tingting_endpoint_spec.md')-m('figures/f5_core_endpoint.png')))
print('model_compare_20260819 mtime=%s ; f4 png mtime=%s ; gap=%.0f s'%(f(m('runs/model_compare_20260819.jsonl')),f(m('figures/f4_fixed_policy.png')),m('runs/model_compare_20260819.jsonl')-m('figures/f4_fixed_policy.png')))
print()
print('=== MANIFEST STATUS ROWS ===')
for l in open(R/'FIGURES_MANIFEST.md'):
    if 'FINAL' in l or 'DRAFT' in l: print('  '+l.rstrip()[:200])
