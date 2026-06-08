#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, html, pathlib

cards = json.load(open('cards.json', encoding='utf-8'))
data_js = json.dumps(cards, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Анатомия и физиология животных — карточки</title>
<style>
  :root{
    --bg:#f4f1ea; --panel:#ffffff; --ink:#2c2a26; --muted:#8a8377;
    --accent:#7c9473; --accent2:#c97b5a; --line:#e6e0d4;
    --know:#7c9473; --learn:#c97b5a; --shadow:0 10px 30px rgba(60,50,30,.12);
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    background:var(--bg);color:var(--ink);line-height:1.55;-webkit-font-smoothing:antialiased}
  header{padding:22px 18px 10px;text-align:center}
  h1{margin:0 0 4px;font-size:22px;font-weight:700;letter-spacing:-.2px}
  .sub{color:var(--muted);font-size:13px;margin:0}
  .wrap{max-width:760px;margin:0 auto;padding:0 16px 80px}
  .bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin:14px 0 6px}
  .bar > i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--accent),#9fb38f);transition:width .3s}
  .stats{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:14px}
  .controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  .controls input,.controls select{flex:1;min-width:130px;padding:10px 12px;border:1px solid var(--line);
    border-radius:12px;background:var(--panel);font-size:14px;color:var(--ink);outline:none}
  .controls input:focus,.controls select:focus{border-color:var(--accent)}
  .toggle{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);
    background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:0 12px;cursor:pointer;user-select:none}
  .toggle input{accent-color:var(--accent);width:16px;height:16px}
  .card{background:var(--panel);border-radius:20px;box-shadow:var(--shadow);border:1px solid var(--line);
    min-height:360px;padding:26px 24px;cursor:pointer;position:relative;display:flex;flex-direction:column;
    transition:transform .12s}
  .card:active{transform:scale(.995)}
  .badge{display:inline-block;align-self:flex-start;font-size:11px;font-weight:600;letter-spacing:.3px;
    text-transform:uppercase;color:var(--accent);background:rgba(124,148,115,.12);
    padding:4px 10px;border-radius:99px;margin-bottom:14px}
  .badge.b-learn{color:var(--learn);background:rgba(201,123,90,.12)}
  .qnum{position:absolute;top:22px;right:22px;font-size:12px;color:var(--muted);font-weight:600}
  .side-label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px}
  .qtext{font-size:20px;font-weight:650;margin:0}
  .atext{font-size:15.5px;white-space:pre-wrap;margin:0}
  .hint{margin-top:auto;padding-top:18px;font-size:12px;color:var(--muted);text-align:center}
  .mark{position:absolute;top:18px;left:18px;font-size:18px}
  .nav{display:flex;align-items:center;gap:10px;margin-top:16px}
  .nav button{flex:1;padding:13px;border:none;border-radius:14px;font-size:15px;font-weight:600;cursor:pointer;
    background:var(--panel);border:1px solid var(--line);color:var(--ink);transition:.12s}
  .nav button:hover{border-color:var(--accent)}
  .nav .counter{flex:0 0 auto;font-size:13px;color:var(--muted);min-width:64px;text-align:center}
  .judge{display:flex;gap:10px;margin-top:10px}
  .judge button{flex:1;padding:13px;border:none;border-radius:14px;font-size:15px;font-weight:650;cursor:pointer;color:#fff}
  .judge .know{background:var(--know)}
  .judge .learn{background:var(--learn)}
  .judge button:active{transform:translateY(1px)}
  .empty{text-align:center;color:var(--muted);padding:60px 0}
  footer{text-align:center;font-size:12px;color:var(--muted);padding:10px 0 30px}
  .reset{background:none;border:none;color:var(--accent2);font-size:12px;cursor:pointer;text-decoration:underline}
  @media(max-width:520px){.qtext{font-size:18px}.atext{font-size:14.5px}.card{padding:22px 18px;min-height:340px}}
</style>
</head>
<body>
<header>
  <h1>Анатомия и физиология животных</h1>
  <p class="sub">96 экзаменационных вопросов · карточки для подготовки</p>
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

  <div id="stage"></div>

  <div class="nav" id="navbox">
    <button id="prev">‹ Назад</button>
    <span class="counter" id="counter">1 / 96</span>
    <button id="next">Вперёд ›</button>
  </div>
  <div class="judge" id="judgebox">
    <button class="learn" id="bLearn">Учить ещё</button>
    <button class="know" id="bKnow">Знаю ✓</button>
  </div>
</div>
<footer>Пробел — перевернуть · ← → листать · собрано для подготовки к экзамену</footer>

<script>
const CARDS = __DATA__;
const LSK = 'anatomy_known_v1';
let known = {};
try{ known = JSON.parse(localStorage.getItem(LSK)||'{}'); }catch(e){ known={}; }

let view = [], idx = 0, flipped = false;

const $ = s => document.querySelector(s);
const stage = $('#stage');

// fill categories
const cats = [...new Set(CARDS.map(c=>c.category))].sort((a,b)=>a.localeCompare(b,'ru'));
const sel = $('#cat');
sel.innerHTML = '<option value="">Все темы ('+CARDS.length+')</option>' +
  cats.map(c=>{const n=CARDS.filter(x=>x.category===c).length;return `<option value="${c}">${c} (${n})</option>`}).join('');

function saveKnown(){ localStorage.setItem(LSK, JSON.stringify(known)); }

function rebuild(){
  const q = $('#search').value.trim().toLowerCase();
  const cat = sel.value;
  const onlyLeft = $('#onlyLeft').checked;
  view = CARDS.filter(c=>{
    if(cat && c.category!==cat) return false;
    if(onlyLeft && known[c.id]) return false;
    if(q && !(c.q.toLowerCase().includes(q) || (''+c.id)===q)) return false;
    return true;
  });
  if(idx>=view.length) idx=0;
  flipped=false;
  render();
  updateStats();
}

function updateStats(){
  const k = CARDS.filter(c=>known[c.id]).length;
  $('#known').textContent = k;
  $('#left').textContent = CARDS.length - k;
  $('#prog').style.width = (k/CARDS.length*100)+'%';
}

function render(){
  if(view.length===0){
    stage.innerHTML = '<div class="card"><div class="empty">Ничего не найдено.<br>Измените поиск или фильтр.</div></div>';
    $('#counter').textContent='0 / 0';
    return;
  }
  const c = view[idx];
  const isKnown = !!known[c.id];
  const badgeClass = isKnown ? 'badge' : 'badge b-learn';
  if(!flipped){
    stage.innerHTML = `<div class="card" id="card">
      <span class="qnum">№ ${c.id}</span>
      ${isKnown?'<span class="mark">✓</span>':''}
      <span class="${badgeClass}">${c.category}</span>
      <div class="side-label">Вопрос</div>
      <p class="qtext">${escapeHtml(c.q)}</p>
      <div class="hint">нажмите, чтобы увидеть ответ · пробел</div>
    </div>`;
  } else {
    stage.innerHTML = `<div class="card" id="card">
      <span class="qnum">№ ${c.id}</span>
      <span class="${badgeClass}">${c.category}</span>
      <div class="side-label">Ответ</div>
      <p class="atext">${escapeHtml(c.a)}</p>
      <div class="hint">нажмите, чтобы вернуться к вопросу</div>
    </div>`;
  }
  $('#card').addEventListener('click', flip);
  $('#counter').textContent = (idx+1)+' / '+view.length;
}

function escapeHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function flip(){ flipped=!flipped; render(); }
function next(){ if(view.length){ idx=(idx+1)%view.length; flipped=false; render(); } }
function prev(){ if(view.length){ idx=(idx-1+view.length)%view.length; flipped=false; render(); } }
function mark(val){
  if(!view.length) return;
  const c=view[idx];
  if(val) known[c.id]=1; else delete known[c.id];
  saveKnown();
  const onlyLeft=$('#onlyLeft').checked;
  if(onlyLeft && val){ rebuild(); } else { next(); updateStats(); }
}

$('#next').onclick=next;
$('#prev').onclick=prev;
$('#bKnow').onclick=()=>mark(true);
$('#bLearn').onclick=()=>mark(false);
$('#search').oninput=rebuild;
sel.onchange=rebuild;
$('#onlyLeft').onchange=rebuild;
$('#reset').onclick=()=>{ if(confirm('Сбросить весь прогресс?')){ known={}; saveKnown(); rebuild(); } };

document.addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT') return;
  if(e.code==='Space'){e.preventDefault();flip();}
  else if(e.code==='ArrowRight') next();
  else if(e.code==='ArrowLeft') prev();
  else if(e.key==='1') mark(false);
  else if(e.key==='2') mark(true);
});

rebuild();
</script>
</body>
</html>"""

out = HTML.replace('__DATA__', data_js)
pathlib.Path('index.html').write_text(out, encoding='utf-8')
print('index.html written,', len(out), 'bytes')
