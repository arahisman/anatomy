#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, pathlib

cards = json.load(open('cards_v2.json', encoding='utf-8'))
data_js = json.dumps(cards, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Анатомия и физиология животных — вопросы</title>
<style>
  :root{
    --bg:#f4f1ea; --panel:#ffffff; --ink:#2c2a26; --muted:#8a8377;
    --accent:#7c9473; --accent2:#c97b5a; --line:#e6e0d4;
    --hint:#c79a3a; --hint-bg:rgba(199,154,58,.10);
    --ans:#7c9473; --ans-bg:rgba(124,148,115,.10);
    --shadow:0 8px 24px rgba(60,50,30,.10);
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    background:var(--bg);color:var(--ink);line-height:1.55;-webkit-font-smoothing:antialiased}
  header.top{padding:22px 18px 8px;text-align:center}
  h1{margin:0 0 4px;font-size:22px;font-weight:700;letter-spacing:-.2px}
  .sub{color:var(--muted);font-size:13px;margin:0}
  .wrap{max-width:780px;margin:0 auto;padding:0 16px 80px}
  .bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin:14px 0 6px}
  .bar > i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--accent),#9fb38f);transition:width .3s}
  .stats{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:14px}
  .reset{background:none;border:none;color:var(--accent2);font-size:12px;cursor:pointer;text-decoration:underline}
  .controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;position:sticky;top:0;z-index:5;
    background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line)}
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
  .card.known{opacity:.62}
  .chead{display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap}
  .num{font-size:12px;font-weight:700;color:var(--muted)}
  .badge{font-size:11px;font-weight:600;letter-spacing:.3px;text-transform:uppercase;color:var(--accent);
    background:rgba(124,148,115,.12);padding:3px 9px;border-radius:99px}
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
  details.hint .body{color:#6b5a2e}
  .empty{text-align:center;color:var(--muted);padding:60px 0}
  footer{text-align:center;font-size:12px;color:var(--muted);padding:10px 0 30px}
  @media(max-width:520px){.q{font-size:16.5px}.card{padding:16px 16px}.details .body{font-size:14.5px}}
</style>
</head>
<body>
<header class="top">
  <h1>Анатомия и физиология животных</h1>
  <p class="sub">96 экзаменационных вопросов · подсказка и ответ к каждому</p>
</header>
<div class="wrap">
  <div class="bar"><i id="prog"></i></div>
  <div class="stats">
    <span><span id="known">0</span> выучено · <span id="left">96</span> осталось</span>
    <button class="reset" id="reset">сбросить прогресс</button>
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
const CARDS = __DATA__;
const LSK = 'anatomy_known_v2';
let known = {};
try{ known = JSON.parse(localStorage.getItem(LSK)||'{}'); }catch(e){ known={}; }

const $ = s => document.querySelector(s);
const list = $('#list');

// categories in source order
const cats = [...new Set(CARDS.map(c=>c.category))];
const sel = $('#cat');
sel.innerHTML = '<option value="">Все темы ('+CARDS.length+')</option>' +
  cats.map(c=>{const n=CARDS.filter(x=>x.category===c).length;return `<option value="${c}">${c} (${n})</option>`}).join('');

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function saveKnown(){ localStorage.setItem(LSK, JSON.stringify(known)); }

// build all cards once
list.innerHTML = CARDS.map(c=>`
  <article class="card${known[c.id]?' known':''}" data-id="${c.id}" data-cat="${esc(c.category)}" data-q="${esc(c.q.toLowerCase())}">
    <div class="chead">
      <span class="num">№ ${c.id}</span>
      <span class="badge">${esc(c.category)}</span>
      <label class="learned"><input type="checkbox" data-id="${c.id}" ${known[c.id]?'checked':''}> выучено</label>
    </div>
    <h2 class="q">${esc(c.q)}</h2>
    <details class="spoiler hint"><summary>💡 Подсказка</summary><div class="body">${esc(c.hint)}</div></details>
    <details class="spoiler ans"><summary>✅ Ответ</summary><div class="body">${esc(c.a)}</div></details>
  </article>`).join('');

function updateStats(){
  const k = CARDS.filter(c=>known[c.id]).length;
  $('#known').textContent = k;
  $('#left').textContent = CARDS.length - k;
  $('#prog').style.width = (k/CARDS.length*100)+'%';
}

function applyFilter(){
  const q = $('#search').value.trim().toLowerCase();
  const cat = sel.value;
  const onlyLeft = $('#onlyLeft').checked;
  let shown = 0;
  document.querySelectorAll('.card').forEach(el=>{
    const id = +el.dataset.id;
    let ok = true;
    if(cat && el.dataset.cat!==cat) ok=false;
    if(onlyLeft && known[id]) ok=false;
    if(q && !(el.dataset.q.includes(q) || (''+id)===q)) ok=false;
    el.style.display = ok ? '' : 'none';
    if(ok) shown++;
  });
  const cnt = $('#count');
  cnt.textContent = shown===CARDS.length ? `Всего вопросов: ${CARDS.length}` : `Показано: ${shown} из ${CARDS.length}`;
  if(shown===0){ if(!$('#empty')){ const d=document.createElement('div'); d.id='empty'; d.className='empty'; d.innerHTML='Ничего не найдено.<br>Измените поиск или фильтр.'; list.appendChild(d);} }
  else { const e=$('#empty'); if(e) e.remove(); }
}

function setAll(selector, open){
  document.querySelectorAll('.card').forEach(card=>{
    if(card.style.display==='none') return;
    const d = card.querySelector(selector);
    if(d) d.open = open;
  });
}

list.addEventListener('change', e=>{
  if(e.target.matches('input[type=checkbox][data-id]')){
    const id = +e.target.dataset.id;
    if(e.target.checked) known[id]=1; else delete known[id];
    saveKnown();
    e.target.closest('.card').classList.toggle('known', !!known[id]);
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
$('#reset').onclick = ()=>{ if(confirm('Сбросить весь прогресс?')){ known={}; saveKnown();
  document.querySelectorAll('.card').forEach(el=>el.classList.remove('known'));
  document.querySelectorAll('input[type=checkbox][data-id]').forEach(cb=>cb.checked=false);
  updateStats(); applyFilter(); } };

updateStats();
applyFilter();
</script>
</body>
</html>"""

out = HTML.replace('__DATA__', data_js)
pathlib.Path('index.html').write_text(out, encoding='utf-8')
print('index.html written,', len(out), 'bytes,', len(cards), 'cards')
