#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds index.html: a 3-section study site (Анатомия / Фармакология / МДК).
Each section is the same list-with-spoilers UI; only the data, theme colour and
filter labels change. Anatomy keeps its original card model and progress key."""
import json, pathlib

def qsort(qid):
    a, b = qid.split('.')
    return (int(a), int(b))

# --- Anatomy: keep original model {id, category, q, hint, a} -> normalized ---
anatomy_src = json.load(open('cards_v2.json', encoding='utf-8'))
anatomy = [{
    "num": str(c["id"]),
    "category": c["category"],
    "q": c["q"],
    "hint": c["hint"],
    "a": c["a"],
} for c in anatomy_src]

# --- Pharma / MDK: object keyed "БИЛЕТ.ВОПРОС" -> grouped by билет ---
def load_tickets(path):
    src = json.load(open(path, encoding='utf-8'))
    out = []
    for qid in sorted(src.keys(), key=qsort):
        v = src[qid]
        ticket = qid.split('.')[0]
        out.append({
            "num": qid,
            "category": f"Билет {ticket}",
            "q": v["ВОПРОС"],
            "hint": v["ПОДСКАЗКА"],
            "a": v["ОТВЕТ"],
        })
    return out

pharma = load_tickets('farma_answers.json')
mdk = load_tickets('mdk_answers.json')

DATA = {"anatomy": anatomy, "pharma": pharma, "mdk": mdk}
data_js = json.dumps(DATA, ensure_ascii=False)

n_anat, n_pharma, n_mdk = len(anatomy), len(pharma), len(mdk)
nb_pharma = len({c["category"] for c in pharma})
nb_mdk = len({c["category"] for c in mdk})

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Экзамены — карточки для подготовки</title>
<style>
  :root{
    --panel:#ffffff; --ink:#2c2a26; --muted:#8a8377; --line:#e6e0d4;
    --hint:#c79a3a; --hint-bg:rgba(199,154,58,.12); --hint-ink:#6b5a2e;
    --ans:#7c9473; --ans-bg:rgba(124,148,115,.12);
    --shadow:0 8px 24px rgba(60,50,30,.10);
    --bg:#f4f1ea; --accent:#7c9473; --accent-soft:rgba(124,148,115,.12);
  }
  /* per-section theming: only background + accent + line tint change */
  body.sec-anatomy{ --bg:#f1f0e6; --accent:#7c9473; --accent-soft:rgba(124,148,115,.13); --line:#e3ddd0; }
  body.sec-pharma { --bg:#f8f1dd; --accent:#bf8f2b; --accent-soft:rgba(191,143,43,.15); --line:#ece2c8; }
  body.sec-mdk    { --bg:#e9eff6; --accent:#5c7fa6; --accent-soft:rgba(92,127,166,.15); --line:#d8e1ec; }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    background:var(--bg);color:var(--ink);line-height:1.55;-webkit-font-smoothing:antialiased;transition:background .35s}
  header.top{padding:18px 18px 6px;text-align:center}
  h1{margin:0 0 4px;font-size:21px;font-weight:700;letter-spacing:-.2px}
  .sub{color:var(--muted);font-size:13px;margin:0}
  .wrap{max-width:780px;margin:0 auto;padding:0 16px 80px}
  /* section tabs */
  .tabs{display:flex;gap:8px;max-width:780px;margin:14px auto 0;padding:0 16px}
  .tabs button{flex:1;padding:11px 8px;border:1px solid var(--line);border-radius:13px 13px 0 0;
    background:var(--panel);color:var(--muted);font-size:14px;font-weight:650;cursor:pointer;
    border-bottom:none;transition:.15s;opacity:.7}
  .tabs button .n{display:block;font-size:11px;font-weight:500;opacity:.8;margin-top:2px}
  .tabs button.active{color:#fff;background:var(--accent);border-color:var(--accent);opacity:1;
    box-shadow:var(--shadow)}
  .tabs button:not(.active):hover{opacity:1;border-color:var(--accent)}
  .bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin:14px 0 6px}
  .bar > i{display:block;height:100%;width:0;background:var(--accent);transition:width .3s}
  .stats{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:14px}
  .reset{background:none;border:none;color:var(--accent);font-size:12px;cursor:pointer;text-decoration:underline}
  .controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;position:sticky;top:0;z-index:5;
    background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);transition:background .35s}
  .controls input,.controls select{flex:1;min-width:130px;padding:10px 12px;border:1px solid var(--line);
    border-radius:12px;background:var(--panel);font-size:14px;color:var(--ink);outline:none}
  .controls input:focus,.controls select:focus{border-color:var(--accent)}
  .toggle{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);
    background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:0 12px;cursor:pointer;user-select:none}
  .toggle input{accent-color:var(--accent);width:16px;height:16px}
  .bulk{display:flex;gap:8px;margin:0 0 16px}
  .bulk button{flex:1;padding:9px;border:1px solid var(--line);border-radius:12px;background:var(--panel);
    color:var(--muted);font-size:13px;font-weight:600;cursor:pointer;transition:.12s}
  .bulk button:hover{border-color:var(--accent);color:var(--ink)}
  .count{font-size:12px;color:var(--muted);margin:0 0 12px}
  .card{background:var(--panel);border-radius:18px;box-shadow:var(--shadow);border:1px solid var(--line);
    padding:18px 20px;margin-bottom:14px;scroll-margin-top:80px}
  .card.known{opacity:.6}
  .chead{display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap}
  .num{font-size:12px;font-weight:700;color:var(--muted)}
  .badge{font-size:11px;font-weight:600;letter-spacing:.3px;text-transform:uppercase;color:var(--accent);
    background:var(--accent-soft);padding:3px 9px;border-radius:99px}
  .learned{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:12px;color:var(--muted);
    cursor:pointer;user-select:none}
  .learned input{accent-color:var(--accent);width:15px;height:15px}
  .q{font-size:18px;font-weight:650;margin:0 0 12px}
  details.spoiler{border:1px solid var(--line);border-radius:13px;margin-top:8px;overflow:hidden}
  details.spoiler summary{list-style:none;cursor:pointer;padding:11px 14px;font-size:14px;font-weight:600;
    display:flex;align-items:center;gap:8px;user-select:none}
  details.spoiler summary::-webkit-details-marker{display:none}
  details.spoiler summary::after{content:"показать";margin-left:auto;font-size:11px;font-weight:500;
    color:var(--muted);text-transform:uppercase;letter-spacing:.3px}
  details.spoiler[open] summary::after{content:"скрыть"}
  details.hint summary{color:var(--hint);background:var(--hint-bg)}
  details.ans summary{color:var(--ans);background:var(--ans-bg)}
  details.spoiler .body{padding:4px 16px 16px;font-size:15px;white-space:pre-wrap}
  details.hint .body{color:var(--hint-ink)}
  .empty{text-align:center;color:var(--muted);padding:60px 0}
  footer{text-align:center;font-size:12px;color:var(--muted);padding:10px 0 30px}
  @media(max-width:520px){.q{font-size:16.5px}.card{padding:16px 16px}details.spoiler .body{font-size:14.5px}
    .tabs button{font-size:13px}}
</style>
</head>
<body class="sec-anatomy">
<div class="tabs" id="tabs"></div>
<header class="top">
  <h1 id="title"></h1>
  <p class="sub" id="sub"></p>
</header>
<div class="wrap">
  <div class="bar"><i id="prog"></i></div>
  <div class="stats">
    <span><span id="known">0</span> выучено · <span id="left">0</span> осталось</span>
    <button class="reset" id="reset">сбросить прогресс раздела</button>
  </div>

  <div class="controls">
    <input id="search" type="search" placeholder="Поиск по вопросам…" autocomplete="off">
    <select id="cat"></select>
    <label class="toggle"><input type="checkbox" id="onlyLeft"> только невыученные</label>
  </div>

  <div class="bulk">
    <button id="openHints">Открыть все подсказки</button>
    <button id="openAns">Открыть все ответы</button>
    <button id="closeAll">Свернуть всё</button>
  </div>

  <p class="count" id="count"></p>
  <div id="list"></div>
</div>
<footer>Сначала загляни в подсказку, попробуй вспомнить — потом проверь себя ответом.</footer>

<script>
const DATA = __DATA__;
const SECTIONS = {
  anatomy: {label:'Анатомия', title:'Анатомия и физиология животных',
            sub:'__N_ANAT__ экзаменационных вопросов · подсказка и ответ к каждому',
            lsk:'anatomy_known_v2', catAll:'Все темы', catNoun:'тем'},
  pharma:  {label:'Фармакология', title:'Ветеринарная фармакология',
            sub:'__NB_PHARMA__ билета · __N_PHARMA__ вопросов · подсказка и ответ',
            lsk:'pharma_known_v1', catAll:'Все билеты', catNoun:'билетов'},
  mdk:     {label:'МДК 01.01', title:'МДК 01.01 — зоогигиена и кормление',
            sub:'__NB_MDK__ билетов · __N_MDK__ вопрос · подсказка и ответ',
            lsk:'mdk_known_v1', catAll:'Все билеты', catNoun:'билетов'},
};
const ORDER = ['anatomy','pharma','mdk'];

const $ = s => document.querySelector(s);
const list = $('#list'), sel = $('#cat');

let cur = localStorage.getItem('active_section');
if(!SECTIONS[cur]) cur = 'anatomy';
let known = {};

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function loadKnown(){ try{ known = JSON.parse(localStorage.getItem(SECTIONS[cur].lsk)||'{}'); }catch(e){ known={}; } }
function saveKnown(){ localStorage.setItem(SECTIONS[cur].lsk, JSON.stringify(known)); }

// build tab bar
$('#tabs').innerHTML = ORDER.map(k=>{
  const s=SECTIONS[k];
  return `<button data-sec="${k}"><span>${s.label}</span><span class="n">${DATA[k].length} вопр.</span></button>`;
}).join('');

function renderList(){
  const cards = DATA[cur];
  list.innerHTML = cards.map(c=>`
    <article class="card${known[c.num]?' known':''}" data-num="${esc(c.num)}" data-cat="${esc(c.category)}" data-q="${esc(c.q.toLowerCase())}">
      <div class="chead">
        <span class="num">№ ${esc(c.num)}</span>
        <span class="badge">${esc(c.category)}</span>
        <label class="learned"><input type="checkbox" data-num="${esc(c.num)}" ${known[c.num]?'checked':''}> выучено</label>
      </div>
      <h2 class="q">${esc(c.q)}</h2>
      <details class="spoiler hint"><summary>💡 Подсказка</summary><div class="body">${esc(c.hint)}</div></details>
      <details class="spoiler ans"><summary>✅ Ответ</summary><div class="body">${esc(c.a)}</div></details>
    </article>`).join('');
}

function fillCats(){
  const s = SECTIONS[cur];
  const cards = DATA[cur];
  const cats = [...new Set(cards.map(c=>c.category))];
  sel.innerHTML = `<option value="">${s.catAll} (${cards.length})</option>` +
    cats.map(c=>{const n=cards.filter(x=>x.category===c).length;return `<option value="${esc(c)}">${esc(c)} (${n})</option>`}).join('');
}

function updateStats(){
  const cards = DATA[cur];
  const k = cards.filter(c=>known[c.num]).length;
  $('#known').textContent = k;
  $('#left').textContent = cards.length - k;
  $('#prog').style.width = (cards.length? k/cards.length*100:0)+'%';
}

function applyFilter(){
  const q = $('#search').value.trim().toLowerCase();
  const cat = sel.value;
  const onlyLeft = $('#onlyLeft').checked;
  let shown = 0;
  document.querySelectorAll('.card').forEach(el=>{
    const num = el.dataset.num;
    let ok = true;
    if(cat && el.dataset.cat!==cat) ok=false;
    if(onlyLeft && known[num]) ok=false;
    if(q && !(el.dataset.q.includes(q) || num.toLowerCase().startsWith(q))) ok=false;
    el.style.display = ok ? '' : 'none';
    if(ok) shown++;
  });
  const total = DATA[cur].length;
  $('#count').textContent = shown===total ? `Всего вопросов: ${total}` : `Показано: ${shown} из ${total}`;
  let e = $('#empty');
  if(shown===0){ if(!e){ e=document.createElement('div'); e.id='empty'; e.className='empty'; e.innerHTML='Ничего не найдено.<br>Измените поиск или фильтр.'; list.appendChild(e);} }
  else if(e){ e.remove(); }
}

function setAll(selector, open){
  document.querySelectorAll('.card').forEach(card=>{
    if(card.style.display==='none') return;
    const d = card.querySelector(selector);
    if(d) d.open = open;
  });
}

function switchSection(name){
  if(!SECTIONS[name]) return;
  cur = name;
  localStorage.setItem('active_section', cur);
  document.body.className = 'sec-'+cur;
  const s = SECTIONS[cur];
  $('#title').textContent = s.title;
  $('#sub').textContent = s.sub;
  document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('active', b.dataset.sec===cur));
  loadKnown();
  renderList();
  fillCats();
  // reset filters on switch
  $('#search').value=''; $('#onlyLeft').checked=false;
  updateStats();
  applyFilter();
  window.scrollTo(0,0);
}

// events
$('#tabs').addEventListener('click', e=>{
  const b = e.target.closest('button[data-sec]');
  if(b) switchSection(b.dataset.sec);
});
list.addEventListener('change', e=>{
  if(e.target.matches('input[type=checkbox][data-num]')){
    const num = e.target.dataset.num;
    if(e.target.checked) known[num]=1; else delete known[num];
    saveKnown();
    e.target.closest('.card').classList.toggle('known', !!known[num]);
    updateStats();
    if($('#onlyLeft').checked) applyFilter();
  }
});
$('#search').oninput = applyFilter;
sel.onchange = applyFilter;
$('#onlyLeft').onchange = applyFilter;
$('#openHints').onclick = ()=>setAll('details.hint', true);
$('#openAns').onclick = ()=>setAll('details.ans', true);
$('#closeAll').onclick = ()=>setAll('details.spoiler', false);
$('#reset').onclick = ()=>{ if(confirm('Сбросить прогресс этого раздела?')){ known={}; saveKnown();
  document.querySelectorAll('.card').forEach(el=>el.classList.remove('known'));
  document.querySelectorAll('input[type=checkbox][data-num]').forEach(cb=>cb.checked=false);
  updateStats(); applyFilter(); } };

switchSection(cur);
</script>
</body>
</html>"""

out = (HTML
  .replace('__DATA__', data_js)
  .replace('__N_ANAT__', str(n_anat))
  .replace('__N_PHARMA__', str(n_pharma))
  .replace('__NB_PHARMA__', str(nb_pharma))
  .replace('__N_MDK__', str(n_mdk))
  .replace('__NB_MDK__', str(nb_mdk)))
pathlib.Path('index.html').write_text(out, encoding='utf-8')
print(f'index.html written, {len(out)} bytes')
print(f'anatomy={n_anat}, pharma={n_pharma} ({nb_pharma} билетов), mdk={n_mdk} ({nb_mdk} билетов)')
