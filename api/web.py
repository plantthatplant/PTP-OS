"""A minimal built-in Gaia Control Center page, served by the API.

Lovable is the official Control Center, but it is not on this machine — so the API serves this
small page so the founder can open a browser and use Gaia today (morning brief, companion,
houses, voice note, answer a question). It is **presentation only**: pure fetch() against the
API, no logic, no reasoning. It is a stopgap/reference, not a replacement for Lovable.

The page is served same-origin; the API key is injected at render time (acceptable for a local,
single-user greenhouse PC — a hosted Lovable uses per-client keys instead).
"""
from __future__ import annotations


def home_page(api_key: str) -> str:
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gaia Control Center</title>
<style>
 body{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:0 auto;padding:18px;background:#0f1410;color:#e8f0e8}
 h1{font-size:20px;margin:0 0 2px} .sub{color:#8aa; margin:0 0 16px;font-size:13px}
 .card{background:#18211a;border:1px solid #26352a;border-radius:12px;padding:14px 16px;margin:12px 0}
 .k{color:#9fb8a4;font-size:12px;text-transform:uppercase;letter-spacing:.05em;margin:0 0 6px}
 .big{font-size:17px;margin:0 0 6px} .muted{color:#9fb8a4;font-size:14px}
 .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}
 .ok{background:#5fbf6a}.degraded{background:#e0b53a}.down{background:#e05a4a}
 button{background:#2a6a3a;color:#fff;border:0;border-radius:8px;padding:8px 12px;font-size:14px;cursor:pointer}
 input{width:100%;box-sizing:border-box;padding:9px;border-radius:8px;border:1px solid #2a3a2e;background:#0f1410;color:#e8f0e8}
 .row{display:flex;gap:8px;margin-top:8px} .house{border-top:1px solid #223; padding:6px 0}
</style></head><body>
<h1>Gaia Control Center</h1>
<p class="sub" id="hdr">connecting…</p>

<div class="card"><div class="k">Health</div><div id="health" class="muted">…</div></div>
<div class="card"><div class="k">Morning Brief</div><div id="brief" class="big">…</div>
  <div id="priority" class="muted"></div><div id="ask" class="muted"></div></div>
<div class="card"><div class="k">Companion</div><div id="companion" class="big">…</div></div>
<div class="card"><div class="k">Greenhouses</div><div id="houses"></div></div>
<div class="card"><div class="k">Answer today's question</div>
  <div id="q" class="muted">…</div>
  <div class="row"><input id="ans" placeholder="your answer (e.g. no, the canopy is dry)">
  <button onclick="answer()">Send</button></div></div>
<div class="card"><div class="k">Voice / note</div>
  <div class="row"><input id="note" placeholder="speak or type an observation…">
  <button onclick="note()">Add</button></div><div id="notemsg" class="muted"></div></div>

<script>
const KEY = "__KEY__";
const H = {headers:{"Authorization":"Bearer "+KEY,"Content-Type":"application/json"}};
const g = async p => (await fetch("/api/v1"+p, H)).json();
const post = async (p,b) => (await fetch("/api/v1"+p,{...H,method:"POST",body:JSON.stringify(b)})).json();
let QID = null;

async function refresh(){
  try{
    const h = await (await fetch("/api/v1/health")).json();
    document.getElementById("health").innerHTML =
      `<span class="dot ${h.status}"></span><b>${h.status}</b> · v${h.version} · up ${Math.floor(h.uptime_seconds/60)}m · `
      + `snapshot ${h.last_snapshot.assembled_at||"—"} (${h.last_snapshot.age_minutes??"?"}m)${h.last_snapshot.stale?" · STALE":""}`;
    document.getElementById("hdr").textContent = "live · collector: "+h.collector;
    const m = await g("/morning");
    document.getElementById("brief").textContent = m.brief;
    document.getElementById("priority").textContent = "Do first: "+m.priority;
    document.getElementById("ask").textContent = "Ask today: "+m.ask_today+"  ·  confidence "+m.confidence;
    const c = await g("/companion");
    document.getElementById("companion").textContent = c.message+"  ["+c.urgency+"]";
    const houses = await g("/houses");
    document.getElementById("houses").innerHTML = houses.map(x=>
      `<div class="house"><b>${x.name}</b> — ${x.status}`+
      (x.climate?` <span class="muted">(${x.climate.air_temperature_c}°C / ${x.climate.humidity_pct}%RH)</span>`:``)+`</div>`).join("");
    const qs = await g("/questions");
    QID = qs.length ? qs[0].id : null;
    document.getElementById("q").textContent = qs.length ? qs[0].text : "nothing worth asking today";
  }catch(e){ document.getElementById("health").textContent = "cannot reach Gaia: "+e; }
}
async function answer(){ if(!QID) return; const r=await post("/questions/"+QID+"/answer",{answer:document.getElementById("ans").value});
  document.getElementById("q").textContent = "answered — confidence "+r.confidence_before+" → "+r.confidence_after; refresh(); }
async function note(){ const t=document.getElementById("note").value; if(!t) return;
  await post("/voice-notes",{text:t,subject:"site"}); document.getElementById("notemsg").textContent="noted ✓"; document.getElementById("note").value=""; }
refresh(); setInterval(refresh, 60000);
</script></body></html>""".replace("__KEY__", api_key)
