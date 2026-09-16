"""Minimal web UI and JSON API for the Meridian demo."""

from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from meridian_iq.config import Settings
from meridian_iq.patterns.multi_agent import run_multi_agent
from meridian_iq.patterns.prompt_agent import DEFAULT_QUESTION, run_prompt_agent

app = FastAPI(
    title="Meridian Tax Advisors IQ Demo",
    version="0.1.0",
    description="A four-IQ grounding demonstration for tax preparation.",
)


def _result_payload(result) -> dict:
    return {
        "question": result.question,
        "answer": result.answer,
        "facts": [item.as_dict() for item in result.facts],
        "trace": [
            {
                "actor": item.actor,
                "action": item.action,
                "sources": item.sources,
            }
            for item in result.trace
        ],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "mode": Settings.from_env().mode}


@app.get("/api/demo/{pattern}")
def demo(
    pattern: str,
    question: str = Query(default=DEFAULT_QUESTION, min_length=5),
) -> dict:
    runner = run_multi_agent if pattern == "multi" else run_prompt_agent
    return _result_payload(runner(question, Settings.from_env()))


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Meridian Tax Advisors | Four-IQ Demo</title>
  <style>
    :root { --ink:#17223b; --blue:#2563eb; --cyan:#06b6d4; --paper:#f7f9fc;
      --line:#dce3ef; --green:#059669; --violet:#7c3aed; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:linear-gradient(135deg,#eef4ff,#f8fbff 55%,#effcf9);
      font:15px/1.55 Inter,Segoe UI,sans-serif; }
    header { padding:32px max(24px,calc((100vw - 1180px)/2)); color:white;
      background:linear-gradient(115deg,#172554,#1d4ed8 58%,#0891b2); }
    header p { max-width:760px; opacity:.9; } h1 { margin:0 0 6px; font-size:34px; }
    main { max-width:1180px; margin:26px auto; padding:0 22px 40px; }
    .question,.card { background:white; border:1px solid var(--line); border-radius:16px;
      box-shadow:0 10px 28px #1e3a5f12; }
    .question { padding:20px; display:grid; grid-template-columns:1fr auto auto; gap:10px; }
    input { width:100%; border:1px solid #bcc9dc; border-radius:10px; padding:12px; font:inherit; }
    button { border:0; border-radius:10px; padding:0 17px; color:white; background:var(--blue);
      font-weight:700; cursor:pointer; } button.secondary { background:var(--violet); }
    .iq-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:18px 0; }
    .iq { padding:14px; border-radius:12px; background:#fff; border-top:4px solid var(--blue); }
    .iq:nth-child(2){border-color:var(--green)} .iq:nth-child(3){border-color:var(--violet)}
    .iq:nth-child(4){border-color:var(--cyan)} .iq b{display:block;font-size:17px}
    .layout { display:grid; grid-template-columns:1.7fr 1fr; gap:16px; }
    .card { padding:22px; min-height:220px; } .card h2 { margin-top:0; }
    .trace { border-left:3px solid var(--cyan); margin:12px 0; padding-left:12px; }
    .fact { border-bottom:1px solid var(--line); padding:10px 0; }
    .pill { border-radius:999px; padding:3px 8px; color:#1d4ed8; background:#e8f0ff;
      font-size:12px; font-weight:700; }
    pre { white-space:pre-wrap; font:14px/1.55 Inter,Segoe UI,sans-serif; }
    #status { padding:10px 0; font-weight:700; color:#52627a; }
    @media(max-width:800px){.question,.layout{grid-template-columns:1fr}.iq-grid{grid-template-columns:1fr 1fr}
      button{height:44px}}
  </style>
</head>
<body>
<header><h1>Meridian Tax Advisors</h1><strong>Microsoft IQ Grounding Command Center</strong>
<p>Follow Alex Rivera's home-sale question through enterprise work context, structured firm data,
curated tax knowledge, and current web grounding.</p></header>
<main>
  <section class="question"><input id="q" aria-label="Client question"
    value="Alex Rivera sold a home this year. What is the capital-gains impact, and do current law changes affect the result?">
    <button onclick="run('prompt')">Prompt agent</button>
    <button class="secondary" onclick="run('multi')">Multi-agent</button></section>
  <div class="iq-grid">
    <div class="iq"><b>Work IQ</b>Client email, Teams, engagement</div>
    <div class="iq"><b>Fabric IQ</b>Basis, filings, income facts</div>
    <div class="iq"><b>Foundry IQ</b>IRS guidance + firm playbooks</div>
    <div class="iq"><b>Web IQ</b>Current thresholds and changes</div>
  </div>
  <div id="status">Choose a pattern to run the grounded analysis.</div>
  <section class="layout">
    <article class="card"><h2>Grounded recommendation</h2><pre id="answer">Results appear here.</pre></article>
    <aside class="card"><h2>Orchestration trace</h2><div id="trace"></div></aside>
  </section>
  <section class="card" style="margin-top:16px"><h2>Evidence ledger</h2><div id="facts"></div></section>
</main>
<script>
async function run(pattern){
  const status=document.getElementById('status'); status.textContent='Running '+pattern+' pattern...';
  const q=encodeURIComponent(document.getElementById('q').value);
  try{
    const r=await fetch('/api/demo/'+pattern+'?question='+q); if(!r.ok) throw new Error(await r.text());
    const d=await r.json(); document.getElementById('answer').textContent=d.answer;
    document.getElementById('trace').innerHTML=d.trace.map(x=>`<div class="trace"><b>${x.actor}</b><br>
      ${x.action}<br><span class="pill">${x.sources.join(' · ')}</span></div>`).join('');
    document.getElementById('facts').innerHTML=d.facts.map(x=>`<div class="fact"><span class="pill">${x.iq}</span>
      <b> ${x.fact.replaceAll('_',' ')}</b><br><small>${x.citation}</small></div>`).join('') ||
      '<p>Live Foundry response contains inline citations.</p>';
    status.textContent='Complete — '+d.trace.length+' orchestration events, '+d.facts.length+' grounded facts.';
  }catch(e){status.textContent='Demo failed: '+e.message}
}
</script>
</body></html>"""
