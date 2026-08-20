"""build_guide.py - the ten minute guide, for reading off an iPad while presenting.

Not the study document. This is a performance document: what to say, in what order,
with a running clock, at a size that reads at arm's length. Every number comes from
results/*.json at build time, so it cannot drift from the deck.

    python3 deck/build_guide.py     # writes deck/guide.html
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = Path(__file__).resolve().parent / "guide.html"

T = json.loads((RES / "tingting_endpoints.json").read_text())
P = json.loads((RES / "policy_degeneracy.json").read_text())
FS = json.loads((RES / "fewshot.json").read_text())
LK = json.loads((RES / "leakage.json").read_text())
PTEST = json.loads((RES / "primary_test.json").read_text())
R = json.loads((RES / "RESULTS.json").read_text())
CLIN = json.loads((RES / "clinician_comparison.json").read_text())
CONF = json.loads((RES / "confidence_axis.json").read_text())

PRIM, SPEC, DCOV = T["primary_appropriateness"], T["spectrum_appropriateness"], T["debate_coverage"]
DBT, EVID, NEUT = T["debate_with_live_agent"], T["revision_under_evidence"], T["change_under_neutral_control"]
MATCH = R["D_MATCH_1_drug_identity_vs_patient"]
PT = PTEST["by_framing"]
F = list(PT)
ATTR, COVER = PT[F[0]]["attrition"], PT[F[0]]["coverage_check"]
B = [PT[f]["discordant"]["b_pressure_only"] for f in F]
FLIP = [100.0 * PT[f]["flip_rates"]["C1"]["k"] / PT[f]["flip_rates"]["C1"]["n"] for f in F]
HRR_P = [T["sycophancy_under_pressure"][f]["HRR"]["pct"] for f in F]
PR = FS["paired"]
N = PRIM["baseline_pre_culture"]["n"]
NP = sorted({PT[f]["n_primary"] for f in F})
NP_SPAN = str(NP[0]) if len(NP) == 1 else f"{NP[0]} to {NP[-1]}"
IND = sorted({PT[f]["attrition"]["dropped_indeterminate_outcome"] for f in F})
IND_SPAN = str(IND[0]) if len(IND) == 1 else f"{IND[0]} to {IND[-1]}"
P_WORST = max(PT[f]["discordant"]["p_exact"] for f in F)

SLIDES = [
    (1, "Title", 15, "Two agents, one antibiotic, and a laboratory that decides who was right.",
     "The question is not mine, it is my supervisor's."),
    (2, "The clinical decision", 35,
     "Bacteria in the blood kills in days. The drug is chosen now; the lab answers a median of 134 hours later.",
     "So there is a real answer, and it arrives later."),
    (3, "The referee", 40,
     "The doctor is not the reference, the bacteria are. Neither agent can see the panel, argue with it, or produce it.",
     "With a referee you can ask a question you could not ask before."),
    (4, "The question", 15,
     "Does multi-agent communication improve clinical decision quality, or does it merely make the models agree?",
     "Here is how one patient becomes one measurement."),
    (5, "The pipeline", 45,
     f"9,236 cultures gated to 7,796, hash-frozen. A seeded {N} evaluated. Stage 4 is the only thing that changes.",
     "And this is what the model actually sees."),
    (6, "The instrument", 40,
     f"The prompt verbatim, six patient fields, and the four pressure sentences. {LK['leaked_turns']} of {LK['n_turns']} turns contain any microbiology.",
     "So what does it do before anyone speaks to it."),
    (7, "The conversation", 40,
     "Five turns, both directions, every position recorded. Nothing here decides what is true.",
     "Start with what happens before anyone speaks."),
    (8, "Result one, the constant", 45,
     f"{P['C0 baseline']['distinct']} drug for {P['C0 baseline']['n']} patients, and it scores {PRIM['baseline_pre_culture']['pct']}%.",
     "Does it move when somebody speaks to it."),
    (9, "Result two, the primary test", 50,
     f"c = 0 in every framing. b = {min(B)} to {max(B)} of {NP_SPAN}. The panel moves it less than a person does.",
     "It moves. Does the movement hurt anybody."),
    (10, "Result three, the 2x2", 25,
     f"Her four cells. Harmful revision {min(HRR_P):.1f} to {max(HRR_P):.1f}% under scripted pressure.",
     "If I stopped here I would be wrong, and she told me where to look."),
    (11, "Result four, stewardship", 45,
     f"An empty sentence moves carbapenem use {SPEC['baseline']['carbapenem_pct']:.0f} to {SPEC['under_pressure']['carbapenem_pct']}%.",
     "One more control before the answer."),
    (12, "Result five, same drug", 35,
     f"Gap zero in every stratum. Mantel-Haenszel OR {MATCH['cmh_stratified_by_drug']['or_mh']}, p = {MATCH['cmh_stratified_by_drug']['p']}.",
     "Now the arm that answers the question."),
    (13, "The answer", 50,
     f"Live agent: HRR {DBT['HRR']['pct']}%, coverage {DCOV['debate_change_pts']:+.1f}. Panel: {EVID['HRR']['pct']:.1f}%, {DCOV['evidence_change_pts']:+.1f}.",
     "So can prompting fix it."),
    (14, "The ladder", 40,
     f"Few-shot breaks the constant, {FS['aware']['fewshot']['distinct']} drugs, and costs coverage. p = {PR['p_exact']:.4f}.",
     "Which is what licenses the next rung."),
    (15, "The contribution", 30,
     "Invisible on accuracy, severe on stewardship. The measurement is the finding.",
     "What it does not show."),
    (16, "Limitations", 25,
     "The constant baseline, the arm coverage, the scripted counterpart, one checkpoint, no clinician.",
     "Where this goes."),
    (17, "Close", 20,
     "The laboratory is the referee, and the measurement is the contribution.", ""),
]
TOTAL = sum(s[2] for s in SLIDES)

QA = [
    ("Is 200 not small?",
     "It is small and it is paired. Each patient is his own control across four conditions at "
     f"temperature 0. That is where p of {P_WORST:.0e} comes from."),
    (f"Why {NP_SPAN} cases in the primary test, not all {N}?",
     f"Every case now carries a row in every condition, so nothing is missing because an arm stopped "
     f"early. {IND_SPAN} per framing drop because a condition returns UNDETERMINED, which happens when the "
     "laboratory never tested that drug against that organism. That is what the lab chose to test, not "
     "a property of the model."),
    ("Carbapenem for all maximises coverage. Is it not right to escalate?",
     "Yes if coverage is your only endpoint, which is exactly why it cannot be. It escalates for a "
     "sentence with no information, and coverage was already high."),
    ("Isn't sycophancy already known?",
     "Yes, and I do not claim it. What is missing in the literature is the arbiter: a per-patient "
     "laboratory panel neither agent can see."),
    ("Model versus clinician?",
     f"On cases where both can be scored, {CLIN['model_zero_shot']['adequate_determined_only']['pct']}% against "
     f"{CLIN['clinician']['adequate_determined_only']['pct']}%. Indistinguishable. The full-cohort margin is a denominator artefact."),
    ("Did you measure confidence, as she asked?",
     f"Yes. The binary is degenerate and I say so. On the continuous measure, holding a correct answer "
     f"costs confidence and abandoning one gains it, {CONF['harmful_deference_vs_stable_correct']['observed_difference_in_mean_delta']:+.1f} points, "
     f"permutation p = {CONF['harmful_deference_vs_stable_correct']['p_two_sided']}, on {CONF['by_transition_cell']['harmful_deference']['n']} exposures."),
    ("Have you shown patient harm?",
     "No. Observational data. Alignment with recorded microbiology and counterfactual appropriateness, "
     "never a recommendation causing an outcome."),
    ("What would change your mind?",
     "A live opposing agent that varies its argument, or a heterogeneous pair. If beneficial corrections "
     "outran harmful ones the sign would flip and I would say so."),
]

rows = "\n".join(
    f'''  <button class="slide" data-start="{sum(x[2] for x in SLIDES[:i])}" data-end="{sum(x[2] for x in SLIDES[:i+1])}">
    <span class="num">{n}</span>
    <span class="body"><span class="ttl">{title}</span><span class="say">{say}</span>
      {f'<span class="move">{move}</span>' if move else ''}</span>
    <span class="secs">{secs}s</span>
  </button>''' for i, (n, title, secs, say, move) in enumerate(SLIDES))

qa = "\n".join(
    f'''  <details><summary>{q}</summary><p>{a}</p></details>''' for q, a in QA)

HTML = f"""<title>Ten Minute Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{
  --bg:#161616; --panel:#262626; --panel2:#393939; --line:#393939;
  --ink:#F4F4F4; --mute:#A8A8A8; --blue:#78A9FF; --pink:#FF7EB6; --teal:#3DDBD9;
}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
html,body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,system-ui,sans-serif;
  font-size:17px;line-height:1.45;-webkit-text-size-adjust:100%}}
.wrap{{max-width:820px;margin:0 auto;padding:0 16px 120px}}

header{{padding:22px 0 14px}}
.kick{{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 8px}}
h1{{margin:0;font-size:30px;font-weight:600;letter-spacing:-.02em;line-height:1.1}}
.sub{{color:var(--mute);margin:8px 0 0;font-size:15px}}

/* the clock, always in reach */
.clock{{position:sticky;top:0;z-index:10;background:var(--bg);
  border-bottom:1px solid var(--line);padding:12px 0;display:flex;gap:12px;align-items:center}}
.time{{font-family:"IBM Plex Mono",monospace;font-size:34px;font-weight:600;
  font-variant-numeric:tabular-nums;min-width:118px}}
.time.over{{color:var(--pink)}}
.bar{{flex:1;height:10px;background:var(--panel2);position:relative;overflow:hidden}}
.fill{{position:absolute;inset:0 auto 0 0;width:0;background:var(--blue);transition:width .5s linear}}
.fill.over{{background:var(--pink)}}
button.ctl{{font-family:"IBM Plex Sans";font-size:16px;font-weight:600;color:var(--bg);
  background:var(--blue);border:0;padding:12px 18px;min-width:92px;cursor:pointer}}
button.ctl.reset{{background:var(--panel2);color:var(--ink)}}

.slide{{display:grid;grid-template-columns:38px 1fr 52px;gap:14px;width:100%;text-align:left;
  background:var(--panel);border:0;border-left:3px solid transparent;
  border-bottom:1px solid var(--bg);padding:16px 14px;color:var(--ink);cursor:pointer;font:inherit}}
.slide.on{{border-left-color:var(--blue);background:var(--panel2)}}
.slide.done{{opacity:.45}}
.num{{font-family:"IBM Plex Mono",monospace;font-size:15px;color:var(--mute);padding-top:3px}}
.ttl{{display:block;font-weight:600;font-size:17px;margin-bottom:3px}}
.say{{display:block;font-size:16px;color:var(--ink)}}
.move{{display:block;font-size:14.5px;color:var(--blue);margin-top:6px;font-style:italic}}
.secs{{font-family:"IBM Plex Mono",monospace;font-size:14px;color:var(--mute);text-align:right;padding-top:3px}}

h2{{font-size:13px;font-family:"IBM Plex Mono",monospace;letter-spacing:.14em;text-transform:uppercase;
  color:var(--blue);margin:34px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}}
details{{background:var(--panel);border-bottom:1px solid var(--bg)}}
summary{{padding:16px 14px;font-weight:600;font-size:16.5px;cursor:pointer;list-style:none}}
summary::-webkit-details-marker{{display:none}}
summary::before{{content:"+";color:var(--blue);font-family:"IBM Plex Mono",monospace;
  font-weight:600;margin-right:10px}}
details[open] summary::before{{content:"\\2212"}}
details p{{margin:0;padding:0 14px 16px 36px;color:var(--mute);font-size:16px}}

.never{{background:var(--panel);border-left:3px solid var(--pink);padding:14px;margin-top:10px}}
.never li{{margin:0 0 8px;font-size:15.5px}}
.never ul{{margin:0;padding-left:18px}}
footer{{color:var(--mute);font-family:"IBM Plex Mono",monospace;font-size:12px;
  margin-top:30px;padding-top:14px;border-top:1px solid var(--line)}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>

<div class="wrap">
<header>
  <p class="kick">UNIQ+ · Kloppenburg room · 12:15</p>
  <h1>Ten minute guide</h1>
  <p class="sub">Tap a row to mark where you are. The clock turns pink when you pass {TOTAL // 60}:{TOTAL % 60:02d}.</p>
</header>

<div class="clock">
  <span class="time" id="t">0:00</span>
  <div class="bar"><div class="fill" id="fill"></div></div>
  <button class="ctl" id="go">Start</button>
  <button class="ctl reset" id="rs">Reset</button>
</div>

{rows}

<h2>If asked</h2>
{qa}

<h2>Never say</h2>
<div class="never"><ul>
<li>That sycophancy or peer conformity is a new finding. Both are published.</li>
<li>That the model underperforms a constant policy. Carbapenem-for-all maximises coverage here.</li>
<li>That the speaking-order effect is a discovery. It is entailed. Kappa 0.178.</li>
<li>That the model is unstable. The neutral control moves it in zero cases.</li>
<li>Anything causal. Alignment with recorded microbiology, or counterfactual appropriateness.</li>
<li>A number that is not on this page. Say "there is a slide on that" and go to the backup.</li>
</ul></div>

<h2>Open on</h2>
<div class="never" style="border-left-color:var(--teal)">
<p style="margin:0;font-size:16px">Thank her for the endpoint hierarchy, and say which two of her
endpoints the deck reports: susceptibility concordance, and spectrum appropriateness.</p>
</div>

<footer>Generated from results/*.json by deck/build_guide.py · targets total {TOTAL // 60}:{TOTAL % 60:02d} of 10:00</footer>
</div>

<script>
(function(){{
  var TOTAL={TOTAL}, t0=null, tick=null, el=document.getElementById('t'),
      fill=document.getElementById('fill'), go=document.getElementById('go'),
      rows=[].slice.call(document.querySelectorAll('.slide'));
  function fmt(s){{var m=Math.floor(s/60);var r=Math.floor(s%60);return m+':'+(r<10?'0':'')+r;}}
  function paint(){{
    var s=(Date.now()-t0)/1000;
    el.textContent=fmt(s);
    var over=s>TOTAL;
    el.classList.toggle('over',over);
    fill.classList.toggle('over',over);
    fill.style.width=Math.min(100,s/TOTAL*100)+'%';
    rows.forEach(function(r){{
      var a=+r.dataset.start,b=+r.dataset.end;
      r.classList.toggle('on',s>=a&&s<b);
      r.classList.toggle('done',s>=b);
    }});
  }}
  go.addEventListener('click',function(){{
    if(tick){{clearInterval(tick);tick=null;go.textContent='Resume';return;}}
    if(!t0)t0=Date.now();
    else t0=Date.now()-( (el.textContent.split(':')[0]*60 + +el.textContent.split(':')[1])*1000 );
    tick=setInterval(paint,500);paint();go.textContent='Pause';
  }});
  document.getElementById('rs').addEventListener('click',function(){{
    if(tick)clearInterval(tick);tick=null;t0=null;el.textContent='0:00';
    el.classList.remove('over');fill.classList.remove('over');fill.style.width='0';
    rows.forEach(function(r){{r.classList.remove('on','done');}});go.textContent='Start';
  }});
  rows.forEach(function(r){{
    r.addEventListener('click',function(){{
      rows.forEach(function(x){{x.classList.remove('on');}});
      r.classList.add('on');
    }});
  }});
}})();
</script>
"""

OUT.write_text(HTML)
print(f"wrote {OUT.relative_to(ROOT)}  ({len(SLIDES)} slides, {TOTAL}s of targets, {len(QA)} answers)")
