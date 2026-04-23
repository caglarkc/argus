// ---------- Helpers ----------
const el = id => document.getElementById(id);
const fileInputA = el('fileInputA');
const fileInputB = el('fileInputB');
const fileNameA  = el('fileNameA');
const fileNameB  = el('fileNameB');
const summaryA   = el('summaryA');
const summaryB   = el('summaryB');
const catalogA   = el('catalogA');
const catalogB   = el('catalogB');
const timelineA  = el('timelineA');
const timelineB  = el('timelineB');
const diffBody   = el('diffBody');

const modal      = el('modal');
const modalTitle = el('modalTitle');
const modalContent = el('modalContent');
const copyBtn = el('copyBtn');
const closeBtn = el('closeBtn');

function md(htmlText){
  const raw = (window.marked && typeof marked.parse==='function')? marked.parse(htmlText||''): (htmlText||'');
  const clean = (window.DOMPurify && DOMPurify.sanitize)? DOMPurify.sanitize(raw): raw;
  const div = document.createElement('div'); div.innerHTML = clean; return div;
}
function codeBlock(text){ const pre = document.createElement('pre'); pre.textContent = text?? ''; return pre; }
function pill(label){ const a=document.createElement('span'); a.className='pill'; a.textContent=label; return a; }
function tag(label){ const s=document.createElement('span'); s.className='tag'; s.textContent=label; return s; }
function pretty(obj){ try{return JSON.stringify(obj,null,2)}catch{return String(obj)} }
function makeSectionCollapsible(title, count, innerNode, open=false){
  const details=document.createElement('details'); details.className='section'; if(open) details.setAttribute('open','');
  const summary=document.createElement('summary'); summary.innerHTML = title + (typeof count==='number'? ` <span class=\"pill badge\">count: ${count}</span>`: '');
  const body=document.createElement('div'); body.className='section-body'; if(innerNode) body.appendChild(innerNode);
  details.appendChild(summary); details.appendChild(body);
  return details;
}
function expandOrCollapseAll(open){
  document.querySelectorAll('details').forEach(d => open? d.setAttribute('open',''): d.removeAttribute('open'));
}
el('expandAllBtn').onclick = () => expandOrCollapseAll(true);
el('collapseAllBtn').onclick = () => expandOrCollapseAll(false);

// ---------- Parsing ----------
function safeParse(raw){ return (typeof raw==='string')? JSON.parse(raw): raw; }
function parseTrajectoryJson(raw){
  const data = safeParse(raw);
  const interactions = Array.isArray(data.llm_interactions)? data.llm_interactions: [];
  const steps = Array.isArray(data.agent_steps)? data.agent_steps: [];
  return { data, interactions, steps };
}

// ---------- Prompt indexing & tagging ----------
function normalizeText(s){ return String(s==null? '': s).trim(); }
function hashStr(s){
  let h=0; for(let i=0;i<s.length;i++){ h = (h<<5)-h + s.charCodeAt(i); h|=0; }
  return Math.abs(h).toString(36);
}
function buildPromptIndex(interactions){
  const map = new Map();
  const order = [];
  const counters = { system:0, user:0, other:0 };
  const add = (role, content) => {
    const text = normalizeText(content);
    if(!text) return null;
    const key = role + '|' + text;
    if(!map.has(key)){
      const idx = role==='system'? counters.system++: role==='user'? counters.user++: counters.other++;
      const label = (role==='system'?'sys_prompts-': role==='user'?'user_prompts-':'other_prompts-') + idx;
      map.set(key, { label, role, text, count:1 });
      order.push(key);
    } else { map.get(key).count++; }
    return map.get(key);
  };
  for(const it of interactions){
    for(const m of it.input_messages||[]){
      const role = (m.role||'').toLowerCase();
      add(role==='system'?'system': role==='user'?'user':'other', m.content);
    }
  }
  const byLabel = {};
  const byText  = {};
  for(const k of order){
    const {label, text, role} = map.get(k);
    byLabel[label] = { role, text };
    byText[role + '|' + hashStr(text)] = label;
  }
  return { byLabel, byText, order: order.map(k=>map.get(k)) };
}
function renderPromptCatalog(holder, index){
  holder.innerHTML='';
  if(!index ||!index.order ||!index.order.length){ holder.textContent='—'; return; }
  const wrap = document.createElement('div');
  wrap.className='chips';
  for(const item of index.order){
    const a = pill(item.label);
    a.dataset.label = item.label;
    a.dataset.role  = item.role;
    a.dataset.text  = item.text;
    a.title = `message (${item.role})`;
    a.addEventListener('click',()=> openModal(item.label + ` (${item.role})`, item.text));
    wrap.appendChild(a);
  }
  holder.appendChild(wrap);
}
function renderMessageItemWithTags(msg, promptIndex){
  const holder=document.createElement('div');
  const bubble=document.createElement('div'); bubble.className='bubble';
  const head=document.createElement('div'); head.className='chips';
  head.appendChild(tag(msg.role||'(role?)'));
  bubble.appendChild(head);
  const contentBox=document.createElement('div'); contentBox.className='small';
  const role = (msg.role||'').toLowerCase();
  const text = normalizeText(msg.content);
  const key = (role==='system'?'system': role==='user'?'user':'other') + '|' + hashStr(text);
  const label = promptIndex?.byText?.[key];
  if(label){
    const a = pill(label);
    a.addEventListener('click',()=> openModal(`${label} (${role})`, text));
    contentBox.appendChild(a);
  }else{
    if (typeof msg.content === 'string'){ contentBox.appendChild(md(msg.content)); }
    else { contentBox.appendChild(codeBlock(pretty(msg.content))); }
  }
  bubble.appendChild(contentBox);
  holder.appendChild(bubble);
  return holder;
}

// ---------- Render blocks ----------
function renderSummaryBlock(target, d){
  target.innerHTML='';
  if(!d){ target.textContent='—'; return; }
  const kv = document.createElement('div'); kv.className='kv';
  const rows = [
    ['Task', d.task?? '—'],
    ['Provider', d.provider?? '—'],
    ['Model', d.model?? '—'],
    ['Max Steps', d.max_steps?? '—'],
    ['Success', String(Boolean(d.success))],
    ['Start Time', d.start_time || '—'],
    ['End Time', d.end_time || '—'],
    ['Execution Time (s)', (typeof d.execution_time==='number'? d.execution_time.toFixed(3): '—')],
    ['LLM Interactions', Array.isArray(d.llm_interactions)? d.llm_interactions.length: 0],
    ['Agent Steps', Array.isArray(d.agent_steps)? d.agent_steps.length: 0],
  ];
  rows.forEach(([k,v])=>{
    const kdiv=document.createElement('div'); kdiv.textContent=k;
    const vdiv=document.createElement('div'); vdiv.appendChild(document.createTextNode(String(v)));
    kv.appendChild(kdiv); kv.appendChild(vdiv);
  });
  const chips = document.createElement('div'); chips.className='chips'; chips.style.marginTop='6px';
  if (d.total_tokens!=null) chips.appendChild(tag(`total:${d.total_tokens}`));
  if (d.total_input_tokens!=null) chips.appendChild(tag(`in:${d.total_input_tokens}`));
  if (d.total_output_tokens!=null) chips.appendChild(tag(`out:${d.total_output_tokens}`));
  if (d.context_tokens!=null) chips.appendChild(tag(`ctx:${d.context_tokens}`));
  target.appendChild(kv); target.appendChild(chips);
}
function renderInteraction(it, idx, promptIndex){
  const details=makeSectionCollapsible(`Interaction #${idx+1} — ${it.model||''} — ${it.current_task||''} — ${it.timestamp||''}`, null, null, false);
  const inner=document.createElement('div'); inner.className='io-grid';
  const left=document.createElement('div');
  const inputTitle=document.createElement('div'); inputTitle.className='section-title'; inputTitle.textContent='Input';
  left.appendChild(inputTitle);
  const msgs = Array.isArray(it.input_messages)? it.input_messages: [];
  const sysWrap=document.createElement('div');
  const userWrap=document.createElement('div');
  const otherWrap=document.createElement('div');
  let sysCount=0,userCount=0,otherCount=0;
  msgs.forEach(m=>{
    const rendered = renderMessageItemWithTags(m, promptIndex);
    const role = (m.role||'').toLowerCase();
    if (role==='system'){ sysWrap.appendChild(rendered); sysCount++; }
    else if (role==='user'){ userWrap.appendChild(rendered); userCount++; }
    else { otherWrap.appendChild(rendered); otherCount++; }
  });
  if (sysCount>0) left.appendChild(makeSectionCollapsible('System', sysCount, sysWrap, false));
  if (userCount>0) left.appendChild(makeSectionCollapsible('User', userCount, userWrap, false));
  if (otherCount>0) left.appendChild(makeSectionCollapsible('Others', otherCount, otherWrap, false));
  const toolsArr = Array.isArray(it.tools_available)? it.tools_available: [];
  if (toolsArr.length){
    const sec=document.createElement('div'); sec.className='small';
    sec.innerHTML='<div class=\"section-title\">Allowed Tools</div>';
    const chips=document.createElement('div'); chips.className='chips';
    toolsArr.forEach(t=>chips.appendChild(tag(t)));
    sec.appendChild(chips); left.appendChild(sec);
  }
  const right=document.createElement('div');
  const outTitle=document.createElement('div'); outTitle.className='section-title'; outTitle.textContent='Output';
  right.appendChild(outTitle);
  const resp = it.response || {};
  if (resp.content!=null){
    const box = document.createElement('div'); box.className='bubble small';
    box.appendChild(md(String(resp.content)));
    right.appendChild(box);
  }
  const rc=document.createElement('div'); rc.className='chips';
  if (resp.finish_reason) rc.appendChild(tag(`stop:${resp.finish_reason}`));
  if (resp.model) rc.appendChild(tag(resp.model));
  const u = resp.usage||{};
  if (u.input_tokens!=null) rc.appendChild(tag(`in:${u.input_tokens}`));
  if (u.output_tokens!=null) rc.appendChild(tag(`out:${u.output_tokens}`));
  if (u.total_tokens!=null) rc.appendChild(tag(`total:${u.total_tokens}`));
  right.appendChild(rc);
  if (resp.tool_calls){
    const tc=document.createElement('div'); tc.className='small';
    tc.innerHTML='<div class=\"section-title\">Tool Calls</div>';
    tc.appendChild(codeBlock(pretty(resp.tool_calls)));
    right.appendChild(tc);
  }
  inner.appendChild(left); inner.appendChild(right);
  const body=document.createElement('div'); body.appendChild(inner);
  details.appendChild(body);
  return details;
}
function renderTimeline(target, interactions, promptIndex){
  target.innerHTML='';
  if (!interactions ||!interactions.length){ target.innerHTML='<div class=\"muted small\">No interactions.</div>'; return; }
  interactions.forEach((it, idx)=> target.appendChild(renderInteraction(it, idx, promptIndex)));
}

// ---------- Diff ----------
function diffPromptCatalogs(idxA, idxB){
  const wrap = document.createElement('div');
  if(!idxA &&!idxB){ wrap.textContent='—'; return wrap; }
  const toSet = (idx)=> new Set(Object.values(idx?.byLabel||{}).map(v=> (v.role + '|' + v.text)));
  const SA = toSet(idxA), SB = toSet(idxB);
  const common = [...SA].filter(x=>SB.has(x));
  const onlyA  = [...SA].filter(x=>!SB.has(x));
  const onlyB  = [...SB].filter(x=>!SA.has(x));
  const mkList = (arr, cls) => {
    const d=document.createElement('div');
    if(!arr.length){ d.innerHTML = '<div class=\"muted\">(none)</div>'; return d; }
    for(const x of arr){
      const [role,text] = x.split('|',2);
      const box=document.createElement('div'); box.className=cls; box.style.margin='6px 0';
      box.appendChild(tag(role));
      const pre=document.createElement('pre'); pre.textContent=text; pre.style.whiteSpace='pre-wrap';
      box.appendChild(pre); d.appendChild(box);
    }
    return d;
  };
  const secCommon = makeSectionCollapsible('Common prompts', common.length, mkList(common,'bubble'), false);
  const secOnlyA  = makeSectionCollapsible('Only in A', onlyA.length, mkList(onlyA,'diff-del'), false);
  const secOnlyB  = makeSectionCollapsible('Only in B', onlyB.length, mkList(onlyB,'diff-add'), false);
  wrap.appendChild(secCommon);
  wrap.appendChild(secOnlyA);
  wrap.appendChild(secOnlyB);
  return wrap;
}
function diffFlows(A, B){
  const wrap=document.createElement('div');
  const n = Math.max(A?.length||0, B?.length||0);
  if(!n){ wrap.innerHTML = '<div class=\"muted small\">No interactions to compare.</div>'; return wrap; }
  for(let i=0;i<n;i++){
    const itA = A?.[i];
    const itB = B?.[i];
    const title = `Step ${i+1}`;
    const inner=document.createElement('div');
    const grid=document.createElement('div'); grid.className='split';
    const side = (it, label)=>{
      const d=document.createElement('div');
      d.innerHTML = `<div class=\\"sideTitle\\">${label}</div>`;
      if(!it){ d.appendChild(md('<span class=\"muted\">(missing)</span>')); return d; }
      const chips=document.createElement('div'); chips.className='chips';
      (it.tools_available||[]).forEach(t=>chips.appendChild(tag(t)));
      d.appendChild(chips);
      const sys = (it.input_messages||[]).filter(m=>m.role==='system').length;
      const usr = (it.input_messages||[]).filter(m=>m.role==='user').length;
      const oth = (it.input_messages||[]).filter(m=>m.role!=='system' && m.role!=='user').length;
      const kv=document.createElement('div'); kv.className='kv';
      [["System msgs",sys],["User msgs",usr],["Other msgs",oth],["Model", it.model||'—'],["Task", it.current_task||'—']].forEach(([k,v])=>{
        const a=document.createElement('div'); a.textContent=k; const b=document.createElement('div'); b.textContent=String(v); kv.appendChild(a); kv.appendChild(b);
      });
      d.appendChild(kv);
      return d;
    };
    grid.appendChild(side(itA,'A'));
    grid.appendChild(side(itB,'B'));
    const sameModel = (itA?.model||'')===(itB?.model||'');
    const sameToolSet = JSON.stringify([...(new Set(itA?.tools_available||[]))].sort()) === JSON.stringify([...(new Set(itB?.tools_available||[]))].sort());
    const sameSysCount = ((itA?.input_messages||[]).filter(m=>m.role==='system').length) === ((itB?.input_messages||[]).filter(m=>m.role==='system').length);
    const sameUserCount = ((itA?.input_messages||[]).filter(m=>m.role==='user').length) === ((itB?.input_messages||[]).filter(m=>m.role==='user').length);
    const flags=document.createElement('div'); flags.className='chips'; flags.style.marginTop='6px';
    flags.appendChild(tag('model: '+(sameModel?'same':'diff')));
    flags.appendChild(tag('tools: '+(sameToolSet?'same':'diff')));
    flags.appendChild(tag('sysCount: '+(sameSysCount?'same':'diff')));
    flags.appendChild(tag('userCount: '+(sameUserCount?'same':'diff')));
    inner.appendChild(grid); inner.appendChild(flags);
    const sec=makeSectionCollapsible(title, null, inner, false);
    wrap.appendChild(sec);
  }
  return wrap;
}

// ---------- Modal ----------
function openModal(title, text){
  modalTitle.textContent = title||'Prompt';
  const raw = (window.marked && typeof marked.parse==='function')? marked.parse(text||''): (text||'');
  const clean = (window.DOMPurify && DOMPurify.sanitize)? DOMPurify.sanitize(raw): raw;
  modalContent.innerHTML = clean;
  modal.classList.add('open');
}
function closeModal(){ modal.classList.remove('open'); }
closeBtn.addEventListener('click', closeModal);
modal.addEventListener('click', (e)=>{ if(e.target===modal) closeModal(); });
copyBtn.addEventListener('click', ()=>{
  const txt = modalContent.innerText || modalContent.textContent || '';
  navigator.clipboard.writeText(txt);
  copyBtn.textContent='Copied!'; setTimeout(()=> copyBtn.textContent='Copy', 900);
});

// ---------- File handling & layout modes ----------
let stateA=null, stateB=null, idxA=null, idxB=null;
function refreshLayout(){
  const dual =!!(stateA && stateB);
  document.body.classList.toggle('mode-dual', dual);
  document.body.classList.toggle('mode-single',!dual);
}
async function handleFile(inputEl, side){
  const file = inputEl.files?.[0];
  if(!file) return;
  (side==='A'?fileNameA:fileNameB).textContent = file.name;
  const text = await file.text();
  const { data, interactions } = parseTrajectoryJson(text);
  if(side==='A'){
    stateA={data, interactions}; idxA = buildPromptIndex(interactions);
    renderSummaryBlock(summaryA, data); renderPromptCatalog(catalogA, idxA); renderTimeline(timelineA, interactions, idxA);
  } else {
    stateB={data, interactions}; idxB = buildPromptIndex(interactions);
    renderSummaryBlock(summaryB, data); renderPromptCatalog(catalogB, idxB); renderTimeline(timelineB, interactions, idxB);
  }
  if(stateA && stateB){
    diffBody.innerHTML='';
    diffBody.appendChild(makeSectionCollapsible('Prompt catalog diff', null, diffPromptCatalogs(idxA, idxB), true));
    diffBody.appendChild(makeSectionCollapsible('Flow diff (by step index)', null, diffFlows(stateA.interactions, stateB.interactions), true));
  }
  refreshLayout();
}
fileInputA.addEventListener('change', ()=> handleFile(fileInputA,'A'));
fileInputB.addEventListener('change', ()=> handleFile(fileInputB,'B'));

