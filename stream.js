/* Activity stream, shared by the Weapons, Armor and Vendors pages.
   Every refresh reads the whole profile, so this tracks weapons AND armor no matter which page is open.
   The page that loads this file provides: PAGE, streamInfo, streamOpen, byId, runAction, pullTo, setLock,
   selChar, setStatus, isGoneError, ent, state, ls, esc, toast, $, auth, bungieAction, scan (and optionally render).
   It also adds the Postmaster button and panel to every page. */
(function(){
  const PM = 215593132;   // Lost Items (postmaster)
  const ARMOR_BUCKETS = new Set([3448274439, 3551918588, 14239492, 20886954, 1585787867]);
  const KINDS = ['weapons', 'armor'];
  const KNAME = { weapons: 'weapons', armor: 'armor' };
  const PAGEOF = { weapons: 'index.html', armor: 'armor.html' };
  const PTITLE = { weapons: 'Weapons', armor: 'Armor' };
  const CLS = ['Titan', 'Hunter', 'Warlock'];

  function load(){ try { return JSON.parse(ls.get('stream') || '[]'); } catch { return []; } }
  function save(a){ ls.set('stream', JSON.stringify(a.slice(0, 200))); }
  function push(evs){ if (!evs.length) return; save(evs.concat(load())); renderStream(); }
  function timeAgo(t){ const s = (Date.now() - t) / 1000; return s < 45 ? 'just now' : s < 3600 ? Math.round(s / 60) + ' min ago' : s < 86400 ? Math.round(s / 3600) + ' h ago' : new Date(t).toLocaleDateString(); }

  // every weapon and armor piece on the account, from the profile any page already loaded
  function gearFromProfile(p){
    const chars = (p.characters && p.characters.data) || {};
    const insts = ((p.itemComponents || {}).instances || {}).data || {};
    const out = [];
    const add = (items, cid, eq) => {
      for (const it of items || []){
        if (!it.itemInstanceId) continue;
        const d = state.defs && state.defs[it.itemHash]; if (!d) continue;
        const kind = d.it === 3 ? 'weapons' : (d.it === 2 && ARMOR_BUCKETS.has(d.b)) ? 'armor' : null;
        if (!kind) continue;
        const inst = insts[it.itemInstanceId] || {};
        const where = cid ? (CLS[(chars[cid] || {}).classType] || 'Character') + (eq ? ' (equipped)' : '') : 'Vault';
        const pm = it.bucketHash === PM;
        out.push({ kind, id: it.itemInstanceId, hash: it.itemHash, name: d.n, icon: d.i, type: d.t, tier: d.tier,
          charId: cid || null, equipped: !!eq, locked: !!(it.state & 1), postmaster: pm, loc: pm ? 'Postmaster (' + where + ')' : where,
          power: inst.primaryStat ? inst.primaryStat.value : 0, gearTier: inst.gearTier || 0 });
      }
    };
    if (p.profileInventory && p.profileInventory.data) add(p.profileInventory.data.items, null, false);
    for (const cid in ((p.characterInventories && p.characterInventories.data) || {})) add(p.characterInventories.data[cid].items, cid, false);
    for (const cid in ((p.characterEquipment && p.characterEquipment.data) || {})) add(p.characterEquipment.data[cid].items, cid, true);
    return out;
  }

  // what you owned at the last refresh, on any page. Older versions kept one list per page, so merge those.
  function loadKnown(){
    try { const k = JSON.parse(ls.get('known:all') || 'null'); if (k && k.ids) return k; } catch {}
    const k = { kinds: {}, ids: {} };
    for (const kind of KINDS){
      try { const o = JSON.parse(ls.get('known:' + kind) || 'null'); if (o){ k.kinds[kind] = true; for (const id in o) k.ids[id] = [o[id], kind]; } } catch {}
    }
    return k;
  }

  const ownInfo = i => (typeof streamInfo === 'function' && i) ? streamInfo(i) : null;
  const basicInfo = g => ({ v: 'new', label: 'New', extra: [g.type, g.gearTier ? 'Tier ' + g.gearTier : '', g.power ? 'Power ' + g.power : ''].filter(Boolean).join(' · ') });
  let openedFromHash = false;
  const SBMAP = { god: 'god', close: 'close', trash: 'trash', exo: 'exotic', keep: 'keep', old: 'legacy', oldx: 'legacy', review: 'review', unr: 'unrated' };
  // New drops of a kind this page can't rate: load that page in a hidden frame (it scans on load and saves
  // verdicts:weapons / verdicts:armor), then the storage event redraws the stream with real labels.
  // At most one frame per kind, at most every 3 minutes, never inside a frame, never near token expiry.
  const labelingKind = {};
  function bgLabel(kind){
    if (window !== window.top || kind === PAGE || labelingKind[kind] || !PAGEOF[kind]) return;
    if (typeof auth === 'undefined' || !auth.valid()) return;
    try { const a = JSON.parse(localStorage.getItem('auth') || 'null'); if (a && a.exp && a.exp - Date.now() < 5 * 60e3) return; } catch {}
    const k = kind === 'weapons' ? 'w' : 'a', key = 'relabelAt:' + k;
    if (document.querySelector('iframe[data-lbl="' + k + '"]')) return;
    if (Date.now() - +(sessionStorage.getItem(key) || 0) < 180e3) return;
    sessionStorage.setItem(key, String(Date.now()));
    const f = document.createElement('iframe');
    f.src = PAGEOF[kind] + '?b=__BUILD__' + (kind === 'weapons' ? '#weapons' : ''); f.dataset.lbl = k; f.setAttribute('aria-hidden', 'true'); f.tabIndex = -1;
    f.style.cssText = 'position:absolute;width:1px;height:1px;left:-9999px;top:0;border:0;opacity:0';
    labelingKind[kind] = f; document.body.appendChild(f);
    const done = () => { if (labelingKind[kind] !== f) return; delete labelingKind[kind]; f.remove(); renderStream(); };
    setTimeout(done, 150e3);
    window.addEventListener('storage', function h(e){ if (e.key === 'verdicts:' + kind){ window.removeEventListener('storage', h); setTimeout(done, 500); } });
    renderStream();
  }

  window.trackDrops = function(p){
    try { pmCapture(p); } catch (e){ console.warn('postmaster', e); }
    try { if (window.rollCapture) window.rollCapture(p); } catch {}
    if (!p || !p.profileInventory || !p.profileInventory.data) return;   // vault hidden: everything there would look dismantled
    const gear = gearFromProfile(p);
    state.gear = new Map(gear.map(g => [g.id, g]));
    const known = loadKnown(), now = Date.now(), evs = [];
    for (const kind of KINDS) if (!known.kinds[kind])
      evs.push({ t: now, kind: 'info', page: kind, text: 'Started tracking your ' + KNAME[kind] + '. New drops and dismantles will show here on every page.' });
    const fresh = gear.filter(g => known.kinds[g.kind] && !(g.id in known.ids));
    fresh.slice(0, 40).forEach(g => {
      const own = g.kind === PAGE ? byId(g.id) : null;
      const inf = ownInfo(own) || basicInfo(g);
      evs.push({ t: now, kind: 'drop', page: g.kind, id: g.id, hash: g.hash, name: g.name, icon: g.icon, v: inf.v, label: inf.label, extra: inf.extra, loc: g.loc, pm: g.postmaster });
    });
    for (const kind of KINDS) if (kind !== PAGE && fresh.some(g => g.kind === kind && !(typeof savedLabel === 'function' && savedLabel(g.id)))) setTimeout(() => bgLabel(kind), 2000);
    if (fresh.length > 40) evs.push({ t: now, kind: 'info', page: PAGE, text: '+' + (fresh.length - 40) + ' more new items not listed' });
    // An item only counts as dismantled when it's missing on two refreshes at least 45 s apart: right after a move
    // (postmaster to vault, character to character) Bungie's profile can briefly leave it out.
    let miss = {}; try { miss = JSON.parse(ls.get('known:miss') || '{}'); } catch {}
    const nextMiss = {}, keep = {};
    for (const kind of KINDS){
      if (!known.kinds[kind]) continue;
      const gone = [];
      for (const id of Object.keys(known.ids)){
        if (known.ids[id][1] !== kind || state.gear.has(id)) continue;
        if (miss[id] && now - miss[id] > 45e3) gone.push(known.ids[id][0]);
        else { nextMiss[id] = miss[id] || now; keep[id] = known.ids[id]; }
      }
      if (gone.length) evs.push({ t: now, kind: 'gone', page: kind, names: gone.slice(0, 30), count: gone.length });
    }
    ls.set('known:miss', JSON.stringify(nextMiss));
    if (fresh.length && !$('streamMute').checked){
      const f = fresh[0], inf = ownInfo(f.kind === PAGE ? byId(f.id) : null);
      toast(fresh.length === 1 ? 'New drop: ' + f.name + (inf ? ' (' + inf.label + ')' : '') + (f.postmaster ? ' in your postmaster' : '') : fresh.length + ' new drops. Open 📡 Activity to see them.');
    }
    ls.set('known:all', JSON.stringify({ kinds: { weapons: true, armor: true }, ids: Object.assign(keep, Object.fromEntries(gear.map(g => [g.id, [g.name, g.kind]]))) }));
    // drops logged on another page get their verdict once this page has rated them
    const all = evs.reverse().concat(load());
    for (const e of all){
      if (e.kind !== 'drop' || e.v !== 'new' || e.page !== PAGE) continue;
      const inf = ownInfo(byId(e.id)); if (inf){ e.v = inf.v; e.label = inf.label; e.extra = inf.extra; }
    }
    save(all); renderStream();
    // "Details" from another page links here with #open=<id>
    const m = /^#open=(\w+)$/.exec(location.hash);
    if (m && !openedFromHash){
      openedFromHash = true;
      try { history.replaceState(null, '', location.pathname); } catch {}
      const it = byId(m[1]); if (it && typeof streamOpen === 'function') streamOpen(it);
    }
  };

  // Pull or lock something this page doesn't list (armor on the Weapons page, anything on the Vendors page)
  async function actOther(act, g, btn){
    if (!state.acct){ setStatus('Scan first.', true); return; }
    btn.disabled = true;
    const label = btn.textContent; btn.textContent = act === 'lock' ? '…' : (g.postmaster ? 'Pulling from postmaster…' : 'Pulling…');
    try {
      if (act === 'lock'){ await setLock(g, !g.locked); toast((g.locked ? 'Locked ' : 'Unlocked ') + g.name); }
      else {
        let target = selChar();
        if (g.kind === 'armor'){   // class armor can only go to a character of that class
          // class from the manifest this page already holds; the full definition only when it isn't there
          const lc = state.defs && state.defs[g.hash] && state.defs[g.hash].c;
          const ct = lc !== undefined && lc !== null ? lc : ((await ent('DestinyInventoryItemDefinition', g.hash)) || {}).classType;
          const want = ct < 3 ? CLS[ct] : '';
          const cur = state.chars.find(c => c.id === target);
          if (want && (!cur || cur.name !== want)){ const m = state.chars.find(c => c.name === want); if (!m) throw new Error('You have no ' + want + ' to pull it to.'); target = m.id; }
        }
        await pullTo(g, target); toast('Pulled ' + g.name + ' to ' + g.loc);
        // keep this page's own list in step (Vault, Character...): update the record it holds, then re-read soon
        const mine = typeof byId === 'function' ? byId(g.id) : null;
        if (mine && mine !== g){ mine.charId = target; mine.postmaster = false; mine.loc = g.loc; if ('where' in mine) mine.where = target; }
        if (typeof render === 'function') try { render(); } catch {}
        if (typeof scan === 'function' && PAGE !== 'weapons' && PAGE !== 'armor') setTimeout(() => scan({ silent: true }), 2500);
      }
    } catch (e){
      if (isGoneError(e)){ state.gear.delete(g.id); toast(g.name + ' is already gone.'); }
      else setStatus(g.name + ': ' + e.message, true);
    } finally { btn.disabled = false; btn.textContent = label; renderStream(); }
  }

  function renderStream(){
    const ev = load(), seen = +(ls.get('streamSeen') || 0);
    const unseen = ev.filter(e => e.t > seen && e.kind !== 'info').length;
    $('streamCount').textContent = unseen; $('streamCount').classList.toggle('hidden', !unseen);
    if ($('stream').classList.contains('hidden')) return;
    const gear = state.gear;
    $('streamList').innerHTML = ev.map(e => {
      const when = '<span class="sw">' + timeAgo(e.t) + '</span>';
      if (e.kind === 'info') return '<div class="sev info">' + esc(e.text) + when + '</div>';
      if (e.kind === 'gone') return '<div class="sev gone">🗑 Dismantled ' + e.count + ' ' + esc(KNAME[e.page] || e.page) + ': ' + esc(e.names.join(', ')) + (e.count > e.names.length ? '…' : '') + when + '</div>';
      const own = e.page === PAGE ? byId(e.id) : null;
      const rec = own || (gear && gear.get(e.id)) || null;
      const kindTag = '<span class="skind">' + (e.page === 'armor' ? 'Armor' : 'Weapon') + '</span>';
      // drops logged as New get the label from the last Weapons / Armor scan as soon as one exists
      let ev_v = e.v, ev_l = e.label;
      const L = (!ev_v || ev_v === 'new') && e.id && typeof savedLabel === 'function' ? savedLabel(e.id) : null;
      if (L){ ev_v = SBMAP[L.cls] || 'new'; ev_l = L.label; }
      else if ((!ev_v || ev_v === 'new') && labelingKind[e.page]) ev_l = 'Rating…';
      const locTxt = rec ? (rec.postmaster ? '📬 ' : '') + esc(rec.loc) : gear ? 'No longer in your inventory' : esc(e.loc || '');
      const details = own ? '<button data-sact="open" data-sid="' + esc(e.id) + '">Details</button>'
        : PAGEOF[e.page] ? '<a href="' + PAGEOF[e.page] + '#open=' + esc(e.id) + '">' + (ev_v === 'new' ? 'Rate it on the ' : 'Details on the ') + PTITLE[e.page] + ' page</a>' : '';
      const sImg = '<img decoding="async" src="' + (e.icon ? 'https://www.bungie.net' + esc(e.icon) : '') + '" alt="">';
      return '<div class="sev drop' + (e.t > seen ? ' unseen' : '') + '"' + (rec && e.id ? ' data-roll="' + esc(e.id) + '" data-rh="' + esc(e.hash || '') + '" title="Hover or click for the full roll"' : '') + '>' + (rec && (rec.gearTier || rec.tier) && typeof tierIcon === 'function' ? tierIcon(sImg, rec.gearTier || rec.tier) : sImg) +
        '<div class="sb-body"><div class="sb-top"><b>' + esc(e.name) + '</b><span>' + kindTag + '<span class="sb sb-' + esc(ev_v) + '">' + esc(ev_l) + '</span></span></div>' +
        '<div class="dim-lbl">' + esc(e.extra || '') + '</div>' +
        (e.page === 'weapons' && typeof savedSplit === 'function' && savedSplit(e.id) ? modeGraph(savedSplit(e.id), { compact: true }) : '') +
        '<div class="sloc' + (rec && rec.postmaster ? ' pm' : '') + '">' + locTxt + when + '</div>' +
        '<div class="sbtn">' + (rec ? '<button class="needauth" data-sact="pull" data-sid="' + esc(e.id) + '">' + (rec.postmaster ? '📬 Pull from postmaster' : 'Pull') + '</button>' +
          '<button class="needauth" data-sact="lock" data-sid="' + esc(e.id) + '">' + (rec.locked ? '🔒 Unlock' : '🔓 Lock') + '</button>' : '') + (rec || !gear ? details : '') + '</div>' +
        '</div></div>';
    }).join('') || '<div class="dim-lbl" style="padding:14px">Nothing yet. Scan, then new drops appear here as auto-refresh finds them.</div>';
    $('streamList').querySelectorAll('[data-sact]').forEach(b => b.onclick = () => {
      // only the Weapons page (weapons) and Armor page (armor) handle their own items; every other page pulls and locks
      // straight from the profile record, so Pull works on Today, Vault, Character, Vendors and Shaders too
      const id = b.dataset.sid, ev = load().find(x => x.id === id), own = ev && ev.page === PAGE ? byId(id) : null;
      if (own && typeof runAction === 'function' && typeof streamOpen === 'function'){ if (b.dataset.sact === 'open') streamOpen(own); else Promise.resolve(runAction(b.dataset.sact, id, b)).then(renderStream); return; }
      const g = state.gear && state.gear.get(id); if (g) actOther(b.dataset.sact, g, b);
    });
  }
  window.renderStream = renderStream;

  $('btnStream').onclick = () => { const s = $('stream'); s.classList.toggle('hidden'); if (!s.classList.contains('hidden') && !document.body.classList.contains('streampinned')){ const pp = $('pmPanel'); if (pp) pp.classList.add('hidden'); } if (!s.classList.contains('hidden')) renderStream(); ls.set('streamSeen', String(Date.now())); setTimeout(renderStream, 50); };
  function setPinned(on){
    document.body.classList.toggle('streampinned', on);
    ls.set('streamPinned', on ? '1' : '0');
    $('streamPin').textContent = on ? '📌 Unpin' : '📌 Pin';
    $('streamPin').classList.toggle('on', on);
    if (on){ $('stream').classList.remove('hidden'); ls.set('streamSeen', String(Date.now())); renderStream(); }
  }
  window.setPinned = setPinned;
  $('streamPin').onclick = () => setPinned(!document.body.classList.contains('streampinned'));
  $('streamClose').onclick = () => { $('stream').classList.add('hidden'); setPinned(false); };
  if (ls.get('streamPinned') === '1') setPinned(true);
  $('streamClear').onclick = () => { save([]); renderStream(); };
  $('streamMute').checked = ls.get('streamMute') === '1';
  $('streamMute').onchange = () => ls.set('streamMute', $('streamMute').checked ? '1' : '0');
  setInterval(renderStream, 30e3);
  window.addEventListener('storage', e => { if (e.key === 'stream' || e.key === 'verdicts:weapons' || e.key === 'verdicts:armor') renderStream(); });
  renderStream();


  /* ---- Postmaster: every character's Lost Items, on every page ----
     Read from the same profile refresh (characterInventories, bucket 215593132). Pull one stack or everything for a
     character with PullFromPostmaster. The postmaster holds 21 items per character; past that, new drops are lost. */
  const PM_CAP = 21;
  let pm = null;                       // { at, chars: [{ id, name, items: [{ id, hash, qty }] }] }
  const pmNames = {};
  function pmCapture(p){
    const chars = (p.characters && p.characters.data) || {}, inv = (p.characterInventories && p.characterInventories.data) || {};
    const insts = ((p.itemComponents || {}).instances || {}).data || {};
    if (!Object.keys(chars).length) return;
    pm = { at: Date.now(), chars: Object.values(chars).sort((a, b) => new Date(b.dateLastPlayed) - new Date(a.dateLastPlayed)).map(c => {
      const all = (inv[c.characterId] || {}).items || [];
      const eq = (((p.characterEquipment && p.characterEquipment.data) || {})[c.characterId] || {}).items || [];
      return { id: c.characterId, name: CLS[c.classType] || 'Character', eq: new Set(eq.map(x => x.bucketHash)),
        items: all.filter(it => it.bucketHash === PM).map(it => ({ id: it.itemInstanceId || '0', hash: it.itemHash, qty: it.quantity || 1 })),
        // what's in this character's inventory (not equipped), so a full bucket can be emptied into the vault
        inv: all.filter(it => it.bucketHash !== PM).map(it => ({ id: it.itemInstanceId || '0', hash: it.itemHash, qty: it.quantity || 1, bucket: it.bucketHash,
          locked: !!(it.state & 1), power: ((insts[it.itemInstanceId] || {}).primaryStat || {}).value || 0 })) };
    }) };
    pmButton(); pmWarn(); if (!$('pmPanel').classList.contains('hidden')) pmRender();
  }
  const pmTotal = () => pm ? pm.chars.reduce((n, c) => n + c.items.length, 0) : 0;
  const pmFull = () => pm ? Math.max(0, ...pm.chars.map(c => c.items.length)) : 0;
  // like DIM: "ALMOST FULL!" from 15 of 21, "FULL!" at 21 (anything past 21 is lost)
  const PM_ALMOST = 15;
  const pmLevel = n => n >= PM_CAP ? 'full' : n >= PM_ALMOST ? 'almost' : '';
  const pmLabel = n => { const l = pmLevel(n); return (l === 'full' ? 'FULL! ' : l === 'almost' ? 'ALMOST FULL! ' : '') + '(' + n + '/' + PM_CAP + ')'; };
  window.pmLevel = pmLevel; window.pmLabel = pmLabel;
  // warn once per session each time a character crosses into almost full or full
  function pmWarn(){
    if (!pm) return;
    const hits = [];
    for (const c of pm.chars){
      const lvl = pmLevel(c.items.length), rank = { '': 0, almost: 1, full: 2 }, key = 'pmWarn_' + c.id;
      let prev = ''; try { prev = sessionStorage.getItem(key) || ''; } catch {}
      if (rank[lvl] > rank[prev]) hits.push(c.name + ' ' + pmLabel(c.items.length));
      try { sessionStorage.setItem(key, lvl); } catch {}
    }
    // after the page has written its own scan message, so the warning isn't overwritten
    if (hits.length) setTimeout(() => setStatus('📬 Postmaster ' + (hits.some(h => /FULL! \(21/.test(h) && !/ALMOST/.test(h)) ? 'full' : 'almost full') + ': ' + hits.join(', ') + '.\nAnything past ' + PM_CAP + ' items is lost. Open 📬 (top right) to collect.', true), 1200);
  }
  function pmDef(h){
    const d = state.defs && state.defs[h];
    if (d && d.n) return { n: d.n, i: d.i };
    if (pmNames[h]) return pmNames[h];
    pmNames[h] = { n: 'Loading…', i: '' };
    ent('DestinyInventoryItemDefinition', h).then(x => { const dp = (x && x.displayProperties) || {}; pmNames[h] = { n: dp.name || 'Item ' + h, i: dp.icon || '' }; if (!$('pmPanel').classList.contains('hidden')) pmRender(); })
      .catch(() => { pmNames[h] = { n: 'Item ' + h, i: '' }; });
    return pmNames[h];
  }
  // header button, next to Activity
  const pmBtn = document.createElement('button');
  pmBtn.className = 'ghost needauth hidden'; pmBtn.id = 'btnPM'; pmBtn.type = 'button'; pmBtn.title = 'Postmaster: pull lost items to your characters';
  $('btnStream').insertAdjacentElement('beforebegin', pmBtn);
  function pmButton(){
    const n = pmTotal(), full = pmFull();
    pmBtn.classList.toggle('hidden', !pm && !auth.valid());
    const lvl = pmLevel(full);
    pmBtn.classList.toggle('pmwarn', lvl === 'almost'); pmBtn.classList.toggle('pmfull', lvl === 'full');
    pmBtn.innerHTML = '📬' + (n ? '<b class="scount' + (lvl ? ' pmhot' : '') + '">' + n + '</b>' : '');
    pmBtn.title = n ? (pm.chars.map(c => c.name + ' ' + pmLabel(c.items.length)).join(' · ')) + (lvl ? '. Past ' + PM_CAP + ', new drops are lost.' : '') : 'Postmaster is empty';
  }
  // panel
  const panel = document.createElement('div');
  panel.id = 'pmPanel'; panel.className = 'stream pmpanel hidden';
  panel.innerHTML = '<div class="stream-head"><b>📬 Postmaster</b><span style="flex:1"></span><button class="ghost" id="pmRefresh" title="Re-read from Bungie">↻</button><button class="ghost" id="pmClose">✕</button></div>' +
    '<div class="dim-lbl" style="padding:0 14px 8px">Lost items on each character. Each postmaster holds ' + PM_CAP + '; anything past that is gone.</div>' +
    '<label class="pmroom" title="When a slot is full, move the lowest rarity, lowest power unlocked item in that slot to the vault, then pull. Locked items are never moved."><input type="checkbox" id="pmMakeRoom"> Make room: when a slot is full, move an unlocked item to the vault first (postmaster pulls and moves to a character)</label><div id="pmList"></div>';
  document.body.appendChild(panel);
  // A pinned Activity panel stays put (the Postmaster opens beside it). An unpinned one steps aside while the
  // Postmaster is open and comes back when it closes, so you never have to click Activity again.
  let streamWasOpen = false;
  const pmClose = () => { panel.classList.add('hidden'); if (streamWasOpen){ streamWasOpen = false; $('stream').classList.remove('hidden'); renderStream(); } };
  pmBtn.onclick = () => {
    if (!panel.classList.contains('hidden')) return pmClose();
    panel.classList.remove('hidden');
    const s = $('stream');
    if (!document.body.classList.contains('streampinned') && !s.classList.contains('hidden')){ streamWasOpen = true; s.classList.add('hidden'); }
    pmRender();
  };
  $('pmClose').onclick = pmClose;
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.classList.contains('hidden') && !document.querySelector('#rollPop:not(.hidden)')) pmClose(); });
  $('pmMakeRoom').checked = ls.get('pmMakeRoom') !== '0';
  $('pmMakeRoom').onchange = () => ls.set('pmMakeRoom', $('pmMakeRoom').checked ? '1' : '0');
  $('pmRefresh').onclick = () => { if (typeof scan === 'function') scan({ silent: true }); };
  const img = p => p ? 'https://www.bungie.net' + esc(p) : '';
  function pmRender(){
    const pmLbl = it => { const L = it.id !== '0' && typeof savedLabel === 'function' ? savedLabel(it.id) : null;
      return L ? '<span class="vlabel ' + L.cls + '" title="' + esc(L.label) + '">' + esc(L.tag) + '</span>' + (L.short ? '<span class="mgshort">' + esc(L.short + ' · ' + modeDecide(L.split).text) + '</span>' : '') : ''; };
    const list = $('pmList');
    if (!pm){ list.innerHTML = '<div class="sev info">Sign in and load the page to read your postmaster.</div>'; return; }
    list.innerHTML = pm.chars.map(c => {
      const n = c.items.length, lvl = pmLevel(n);
      return '<div class="pmchar ' + lvl + '"><div class="pmhead"><b>' + esc(c.name) + '</b><span class="pmcount' + (lvl ? ' hot' : '') + '">' + pmLabel(n) + '</span><span style="flex:1"></span>' +
        (n ? '<button class="ghost pmall" data-pmall="' + esc(c.id) + '" title="Pull everything to your ' + esc(c.name) + '">Pull all</button><button class="ghost pmall" data-pmallv="' + esc(c.id) + '" title="Send everything that can go to the vault there (pulled through your ' + esc(c.name) + ')">All to vault</button>' : '') + '</div>' +
        (n ? c.items.map((it, ix) => { const d = pmDef(it.hash);
          return '<div class="pmrow"' + (it.id !== '0' ? ' data-roll="' + esc(it.id) + '" data-rh="' + it.hash + '"' : '') + '>' + (d.i ? '<img decoding="async" src="' + img(d.i) + '" alt="">' : '<span class="pmnoimg"></span>') + '<span class="pmname">' + esc(d.n) + (it.qty > 1 ? ' <span class="dim-lbl">×' + it.qty + '</span>' : '') + pmLbl(it) + '</span>' +
            '<button class="ghost pmone" data-pmc="' + esc(c.id) + '" data-pmi="' + ix + '" title="Pull to your ' + esc(c.name) + '">Pull</button><button class="ghost pmone" data-pmc="' + esc(c.id) + '" data-pmv="' + ix + '" title="Send to the vault">Vault</button></div>'; }).join('')
          : '<div class="dim-lbl pmempty">Empty</div>') + '</div>';
    }).join('') + '<div class="dim-lbl" style="padding:6px 4px">Read ' + new Date(pm.at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) + '</div>';
    list.querySelectorAll('[data-pmi]').forEach(b => b.onclick = () => pmPull(b.dataset.pmc, [c => c.items[+b.dataset.pmi]], b));
    list.querySelectorAll('[data-pmall]').forEach(b => b.onclick = () => pmPull(b.dataset.pmall, null, b));
    list.querySelectorAll('[data-pmv]').forEach(b => b.onclick = () => pmPull(b.dataset.pmc, [c => c.items[+b.dataset.pmv]], b, true));
    list.querySelectorAll('[data-pmallv]').forEach(b => b.onclick = () => pmPull(b.dataset.pmallv, null, b, true));
  }
  let pmBusy = false;
  const NO_ROOM = /no item slots|NoRoomInDestination|no room/i;
  // buckets whose items can't go to the vault: Engrams, Pursuits (quests and bounties), Subclass, Clan banners
  const NO_VAULT = new Set([375726501, 1345459588, 3284755031, 4292445962]);
  const makeRoomOn = () => ls.get('pmMakeRoom') !== '0';
  // which inventory bucket a postmaster item goes to
  async function destBucket(h){
    const d = state.defs && state.defs[h];
    if (d && d.b) return d.b;
    try { const x = await ent('DestinyInventoryItemDefinition', h); return ((x && x.inventory) || {}).bucketTypeHash || 0; } catch { return 0; }
  }
  // free one slot in that bucket: move the least valuable unlocked item there to the vault
  async function makeRoom(ch, bucket){
    if (!bucket || NO_VAULT.has(bucket)) return { err: bucket === 375726501 ? 'your engrams are full (open some in game)' : 'that slot can\'t be emptied into the vault' };
    const rank = x => { const d = state.defs && state.defs[x.hash]; return [(d && d.tier) || 0, x.power]; };
    const cands = ch.inv.filter(x => x.bucket === bucket && !x.locked)
      .sort((a, b) => { const ra = rank(a), rb = rank(b); return ra[0] - rb[0] || ra[1] - rb[1]; });
    if (!cands.length) return { err: 'everything in that slot on your ' + ch.name + ' is locked' };
    const x = cands[0];
    try {
      await bungieAction('/Destiny2/Actions/Items/TransferItem/', { itemReferenceHash: x.hash, stackSize: x.qty, transferToVault: true, itemId: x.id, characterId: ch.id, membershipType: state.acct.membershipType });
    } catch (e){ return { err: NO_ROOM.test(e.message || '') ? 'your vault is full too' : 'couldn\'t move ' + pmDef(x.hash).n + ' to the vault (' + e.message + ')' }; }
    ch.inv = ch.inv.filter(y => y !== x);
    const g = x.id !== '0' && state.gear && state.gear.get(x.id); if (g){ g.charId = null; g.loc = 'Vault'; }
    const own = x.id !== '0' && typeof byId === 'function' ? byId(x.id) : null; if (own){ own.charId = null; own.loc = 'Vault'; if ('where' in own) own.where = 'vault'; }
    return { moved: pmDef(x.hash).n + (x.qty > 1 ? ' ×' + x.qty : '') };
  }
  // Is that bucket on the character already full? Bucket sizes come from DestinyInventoryBucketDefinition
  // (itemCount includes the equipped item for equippable buckets). Only used for instanced items: a stack can merge
  // into one the character already has, so stacks rely on Bungie's no-room answer instead.
  async function bucketFull(ch, bucket){
    if (!bucket) return false;
    let d = null; try { d = await ent('DestinyInventoryBucketDefinition', bucket); } catch {}
    const cap = d && d.itemCount; if (!cap) return false;
    const used = ch.inv.filter(x => x.bucket === bucket).length + (d.category === 3 && ch.eq && ch.eq.has(bucket) ? 1 : 0);
    return used >= cap;
  }
  // make room for one postmaster item on a character, before the pull (force = Bungie already said there's no room)
  async function ensureRoom(cid, hash, instanced, force){
    if (!pm || ls.get('pmMakeRoom') === '0') return {};
    const ch = pm.chars.find(c => c.id === cid); if (!ch) return {};
    const bucket = await destBucket(hash);
    if (!force && !(instanced && await bucketFull(ch, bucket))) return {};
    return makeRoom(ch, bucket);
  }
  // after a pull the item takes a slot: keep the count right for the next item in Pull all
  function landed(cid, it, bucket){ const ch = pm && pm.chars.find(c => c.id === cid); if (!ch) return;
    ch.items = ch.items.filter(x => !(x.id === it.id && x.hash === it.hash && (it.id !== '0' || x.qty === it.qty)));
    if (bucket) ch.inv.push({ id: it.id, hash: it.hash, qty: it.qty, bucket, locked: false, power: 0 });
    pmButton(); if (!$('pmPanel').classList.contains('hidden')) pmRender(); }
  // the item cards on Weapons, Armor and Vault pull from the postmaster through this too
  window.pmEnsureRoom = (cid, hash, instanced, force) => ensureRoom(cid, hash, instanced, force);
  window.pmIsNoRoom = e => NO_ROOM.test((e && e.message) || '');
  // Character page postmaster card: send one item to the vault through the same path
  window.pmToVault = (cid, id, hash, btn) => { const ch = pm && pm.chars.find(c => c.id === cid); if (!ch) return Promise.resolve();
    const ix = ch.items.findIndex(x => x.hash === hash && (!id || x.id === id)); if (ix < 0) return Promise.resolve();
    return pmPull(cid, [c => c.items[ix]], btn || document.createElement('button'), true); };
  window.pmLanded = async (cid, it) => landed(cid, it, await destBucket(it.hash));
  // an item left a character (sent to the vault): free its slot in the model
  window.pmLeft = (cid, id) => { const ch = pm && pm.chars.find(c => c.id === cid); if (ch && id) ch.inv = ch.inv.filter(x => x.id !== id); };
  // Bungie has no direct postmaster-to-vault move: "Vault" pulls the item to that character first, then sends it on
  // to the vault (the same two steps the game does). Engrams and quest items can't go to the vault, so they stay put.
  async function pmPull(cid, pick, btn, toVault){
    if (pmBusy) return;
    if (!state.acct || !auth.valid()){ setStatus('Sign in with Bungie (top right) to pull from the postmaster.', true); return; }
    const ch = pm.chars.find(c => c.id === cid); if (!ch) return;
    const items = pick ? pick.map(f => f(ch)).filter(Boolean) : ch.items.slice();
    pmBusy = true; btn.disabled = true; btn.textContent = '…';
    let ok = 0, vaulted = 0; const fails = [], moved = [];
    const pull = it => bungieAction('/Destiny2/Actions/Items/PullFromPostmaster/', { itemReferenceHash: it.hash, stackSize: it.qty, itemId: it.id, characterId: cid, membershipType: state.acct.membershipType });
    for (const it of items){
      try {
        const bucket = await destBucket(it.hash);
        if (toVault && NO_VAULT.has(bucket)) throw new Error('NoRoom: ' + (bucket === 375726501 ? 'engrams' : 'this') + ' can\'t go to the vault (use Pull instead)');
        // empty a slot first when we can already see the bucket is full
        const pre = await ensureRoom(cid, it.hash, it.id !== '0', false);
        if (pre.err) throw new Error('NoRoom: ' + pre.err);
        if (pre.moved){ moved.push(pre.moved); await new Promise(res => setTimeout(res, 300)); }
        try { await pull(it); }
        catch (e){
          if (!NO_ROOM.test(e.message || '') || !makeRoomOn()) throw e;
          const r = await ensureRoom(cid, it.hash, it.id !== '0', true);
          if (r.err) throw new Error('NoRoom: ' + r.err);
          if (r.moved) moved.push(r.moved);
          await new Promise(res => setTimeout(res, 300));
          await pull(it);
        }
        landed(cid, it, bucket); ok++;
        if (toVault){
          await new Promise(res => setTimeout(res, 300));
          try {
            await bungieAction('/Destiny2/Actions/Items/TransferItem/', { itemReferenceHash: it.hash, stackSize: it.qty, transferToVault: true, itemId: it.id, characterId: cid, membershipType: state.acct.membershipType });
            ch.inv = ch.inv.filter(x => !(x.id === it.id && x.hash === it.hash)); vaulted++;
            const gv = it.id !== '0' && state.gear && state.gear.get(it.id); if (gv){ gv.charId = null; gv.loc = 'Vault'; }
            const ov = it.id !== '0' && typeof byId === 'function' ? byId(it.id) : null; if (ov){ ov.charId = null; ov.postmaster = false; ov.loc = 'Vault'; if ('where' in ov) ov.where = 'vault'; }
          } catch (e){ fails.push(pmDef(it.hash).n + ': pulled to your ' + ch.name + ' but couldn\'t go on to the vault (' + (NO_ROOM.test(e.message || '') ? 'vault full' : e.message) + ')'); }
          continue;
        }
        const g = it.id !== '0' && state.gear && state.gear.get(it.id); if (g){ g.postmaster = false; g.loc = ch.name; }
        const own = it.id !== '0' && typeof byId === 'function' ? byId(it.id) : null; if (own){ own.postmaster = false; own.loc = ch.name; if ('where' in own) own.where = cid; }
      } catch (e){
        const m = e.message || '';
        const why = /^NoRoom: /.test(m) ? m.slice(8) : NO_ROOM.test(m) ? 'no room on your ' + ch.name + (makeRoomOn() ? '' : ' (turn on "Make room" to move something to the vault)') : /cannot|not allowed|NotTransferrable/i.test(m) ? 'can\'t be pulled (pick it up in game)' : m;
        fails.push(pmDef(it.hash).n + ': ' + why);
      }
      await new Promise(r => setTimeout(r, 250));
    }
    pmBusy = false; pmButton(); pmRender();
    if (toVault && vaulted) toast('Sent ' + vaulted + ' item' + (vaulted > 1 ? 's' : '') + ' from the postmaster to the vault');
    else if (ok && !toVault) toast('Pulled ' + ok + ' item' + (ok > 1 ? 's' : '') + ' to your ' + ch.name + (moved.length ? ', moved ' + moved.length + ' to the vault to make room' : ''));
    if (fails.length) setStatus((moved.length ? 'Moved to the vault to make room: ' + moved.join(', ') + '\n' : '') + 'Some items stayed in the postmaster:\n' + fails.slice(0, 6).join('\n') + (fails.length > 6 ? '\n+' + (fails.length - 6) + ' more' : ''), true);
    else if (moved.length) setStatus('Moved to the vault to make room: ' + moved.join(', '));
    if ((ok || moved.length) && typeof render === 'function') try { render(); } catch {}
  }

  /* ---- roll inspector: hover (mouse) or tap any element with data-roll="<itemInstanceId>" data-rh="<itemHash>" ----
     Used by the Postmaster panel and the Vault page. Reads the one item with components 300 (instance), 304 (stats)
     and 305 (sockets), then names the plugs and stats from the manifest. Cached per item for the life of the page. */
  const rollCache = new Map();
  const SKIP_PLUG = /shader|skins|tracker|memento|transmat|ornament|crafting\.|v400\.empty|\.empty|deprecated|weapon_frame_default|enhancements\.universal/i;
  const NOBAR = new Set([4284893193, 3871231066, 447667954, 2961396640, 1931675084, 2715839340, 925767036]);
  const POWER_STAT_H = 1935470627;
  const rpop = document.createElement('div'); rpop.className = 'rollpop hidden'; rpop.id = 'rollPop'; document.body.appendChild(rpop);
  // ---- speed: DIM-style. Pages that load profile components 304/305/310 hand every roll to trackDrops, so most
  // popups need no request at all. Plug names, icons and types come from the lite manifest each page already has
  // (state.defs), so the card draws at once; full definitions (descriptions, editable mod sockets) fill in after
  // from the IndexedDB cache or Bungie, and the card redraws in place.
  let profIC = null;
  const profChar = {}, statNames = {};
  window.rollCapture = function(p){
    const ic = (p && p.itemComponents) || {};
    if (!ic.sockets || !ic.sockets.data) return;
    profIC = { sockets: ic.sockets.data, reuse: (ic.reusablePlugs || {}).data || {}, stats: (ic.stats || {}).data || {}, inst: (ic.instances || {}).data || {} };
    for (const k of ['characterInventories', 'characterEquipment']){ const d = (p[k] || {}).data || {}; for (const cid in d) for (const it of d[cid].items || []) if (it.itemInstanceId) profChar[it.itemInstanceId] = cid; }
    rollCache.clear();
    // stat names for every stat on every item, in the background, so the first card doesn't wait for them
    const keys = new Set(); for (const id in profIC.stats) for (const k in (profIC.stats[id].stats || {})) keys.add(+k);
    const go = () => ensureStatNames([...keys]);
    (window.requestIdleCallback || setTimeout)(go, 300);
  };
  const LITE_CAT = t => /shader/i.test(t) ? 'shader' : /ornament/i.test(t) ? 'ornament' : /tracker/i.test(t) ? 'tracker' : /memento/i.test(t) ? 'memento' : /transmat/i.test(t) ? 'transmat'
    : /intrinsic/i.test(t) ? 'intrinsics' : /masterwork/i.test(t) ? 'masterwork' : /origin/i.test(t) ? 'origin' : /catalyst/i.test(t) ? 'catalyst' : '';
  const RAR_NAME = { 6: 'Exotic', 5: 'Legendary', 4: 'Rare', 3: 'Uncommon', 2: 'Common' };
  async function ensureStatNames(keys){
    const miss = keys.filter(h => !(h in statNames));
    if (miss.length){ try { const d = await entMany('DestinyStatDefinition', miss); for (const h of miss) statNames[h] = ((d[h] || {}).displayProperties || {}).name || ''; } catch { for (const h of miss) statNames[h] = statNames[h] || ''; } }
  }
  function buildRoll(id, hash, src, P, entries, head){
    const { sockets, reuse, stats, ins } = src, rows = [];
    sockets.forEach((x, ix) => {
      if (!x.plugHash || x.isVisible === false) return;
      const act = P(x.plugHash); if (!act || SKIP_PLUG.test(act.cat)) return;
      const opts = (reuse[ix] || []).map(o => Object.assign(P(o.plugItemHash) || {}, { can: o.canInsert !== false && o.enabled !== false })).filter(o => o.n && !SKIP_PLUG.test(o.cat || ''));
      const kind = /intrinsic/i.test(act.cat) ? 'frame' : opts.length > 1 ? 'perk' : 'mod';
      const set = (entries[ix] || {}).reusablePlugSetHash || 0;
      const editable = kind === 'mod' && !!set && !/masterwork|intrinsic|origin|catalyst|tracker/i.test(act.cat);
      if (/^(Empty|Default) /i.test(act.n) && !editable) return;
      rows.push({ ix, act, opts: kind === 'perk' ? opts : [], kind, set: editable ? set : 0, empty: /^Empty /i.test(act.n) });
    });
    const st = Object.values(stats).filter(x => x.statHash !== POWER_STAT_H).map(x => ({ h: x.statHash, n: statNames[x.statHash] || '', v: x.value })).filter(x => x.n);
    return { id, hash, charId: src.charId, name: head.name, icon: head.icon, type: head.type, power: ins.primaryStat ? ins.primaryStat.value : 0, tier: ins.gearTier || 0, rows, stats: st };
  }
  async function fullRoll(id, hash, src, hashes){
    const [plugs, item] = await Promise.all([
      hashes.size ? entMany('DestinyInventoryItemDefinition', [...hashes]) : {},
      ent('DestinyInventoryItemDefinition', hash).catch(() => null)]);
    const P = h => { const d = plugs[h]; if (!d || !(d.displayProperties || {}).name) return null; const cat = ((d.plug || {}).plugCategoryIdentifier) || '';
      return { h, n: d.displayProperties.name, i: d.displayProperties.icon || '', t: d.itemTypeDisplayName || '', desc: d.displayProperties.description || '', enh: /enhanced/i.test(d.itemTypeDisplayName || ''), cat }; };
    const dp = (item && item.displayProperties) || {};
    return buildRoll(id, hash, src, P, ((item && item.sockets) || {}).socketEntries || [], { name: dp.name || pmDef(hash).n, icon: dp.icon || '', type: (item && item.itemTypeAndTierDisplayName) || '' });
  }
  async function readRoll(id, hash){
    if (rollCache.has(id)) return rollCache.get(id);
    const job = (async () => {
      if (!state.acct || !auth.valid()) throw new Error('Sign in to see the roll.');
      let src;
      const c = profIC && profIC.sockets[id];
      if (c && profIC.stats[id]) src = { sockets: c.sockets || [], reuse: (profIC.reuse[id] || {}).plugs || {}, stats: (profIC.stats[id] || {}).stats || {}, ins: profIC.inst[id] || {}, charId: profChar[id] || null };
      else {
        // 300 instance, 304 stats, 305 sockets, 310 reusable plugs (the other perks you can switch to, like DIM's columns)
        const r = await bungie('/Destiny2/' + state.acct.membershipType + '/Profile/' + state.acct.membershipId + '/Item/' + id + '/?components=300,304,305,310');
        src = { sockets: ((r.sockets || {}).data || {}).sockets || [], reuse: ((r.reusablePlugs || {}).data || {}).plugs || {}, stats: ((r.stats || {}).data || {}).stats || {}, ins: (r.instance || {}).data || {}, charId: r.characterId || null };
      }
      const hashes = new Set();
      src.sockets.forEach((x, ix) => { if (x.plugHash) hashes.add(x.plugHash); (src.reuse[ix] || []).forEach(o => hashes.add(o.plugItemHash)); });
      await ensureStatNames(Object.keys(src.stats).map(Number));
      const L = state.defs || {}, lite = h => L[h] && L[h].n;
      if (lite(hash) && [...hashes].every(lite)){
        const P = h => { const d = L[h]; return d && d.n ? { h, n: d.n, i: d.i || '', t: d.t || '', desc: '', enh: /enhanced/i.test(d.t || ''), cat: LITE_CAT(d.t || '') } : null; };
        const d = L[hash];
        const fast = buildRoll(id, hash, src, P, [], { name: d.n, icon: d.i || '', type: [RAR_NAME[d.tier], d.t].filter(Boolean).join(' ') });
        // descriptions and editable mod sockets: fill in, then redraw the open card in place (unless a mod list is open)
        fullRoll(id, hash, src, hashes).then(full => {
          if (rollCache.get(id) !== job) return;
          rollCache.set(id, Promise.resolve(full));
          document.querySelectorAll('[data-rollbox="' + CSS.escape(id) + '"]').forEach(box => { if (!box.querySelector('.rp-modlist:not(.hidden)')) box.outerHTML = rollHtml(full); });
        }).catch(() => {});
        return fast;
      }
      return fullRoll(id, hash, src, hashes);
    })();
    rollCache.set(id, job);
    job.catch(() => rollCache.delete(id));
    return job;
  }
  const pic = (o, cls) => o.i ? '<img decoding="async" class="' + (cls || '') + '" src="' + img(o.i) + '" alt="">' : '<span class="rp-noimg ' + (cls || '') + '"></span>';
  function rollHtml(x){
    const frame = x.rows.filter(r => r.kind === 'frame'), perks = x.rows.filter(r => r.kind === 'perk'), mods = x.rows.filter(r => r.kind === 'mod');
    const swap = (r, o) => esc(x.id + '|' + r.ix + '|' + o.h + '|' + x.hash);
    return '<div class="rp" data-rollbox="' + esc(x.id) + '"><div class="rp-head">' + (x.icon ? (typeof tierIcon === 'function' ? tierIcon('<img decoding="async" src="' + img(x.icon) + '" alt="">', x.tier) : '<img decoding="async" src="' + img(x.icon) + '" alt="">') : '') + '<div><b>' + esc(x.name) + '</b><span>' + esc([x.type, x.tier ? 'Tier ' + x.tier : '', x.power ? 'Power ' + x.power : ''].filter(Boolean).join(' · ')) + '</span></div></div>' +
      (typeof savedSplit === 'function' && savedSplit(x.id) ? modeGraph(savedSplit(x.id)) : '') +
      (x.stats.length ? '<div class="rp-stats">' + x.stats.map(s => '<div class="rp-stat"><span>' + esc(s.n) + '</span>' + (NOBAR.has(s.h) || s.v > 100 ? '<i class="nobar"></i>' : '<i><em style="width:' + Math.max(0, Math.min(100, s.v)) + '%"></em></i>') + '<b>' + s.v + '</b></div>').join('') + '</div>' : '') +
      frame.map(r => '<div class="rp-frame" title="' + esc(r.act.desc) + '">' + pic(r.act) + '<span><b>' + esc(r.act.n) + '</b><small>' + esc(r.act.t) + '</small></span></div>').join('') +
      (perks.length ? '<div class="rp-cols">' + perks.map(r => '<div class="rp-col"><div class="rp-cur' + (r.act.enh ? ' enh' : '') + '" title="' + esc(r.act.desc) + '">' + pic(r.act) + '<span><b>' + esc(r.act.n) + '</b><small>' + esc(r.act.t) + '</small></span></div>' +
          '<div class="rp-alts">' + r.opts.filter(o => o.h !== r.act.h).map(o => '<button class="rp-alt' + (o.enh ? ' enh' : '') + '"' + (o.can ? ' data-swap="' + swap(r, o) + '"' : ' disabled') + ' title="' + esc(o.n + (o.desc ? ': ' + o.desc : '') + (o.can ? '\nClick to switch to this perk' : '')) + '">' + pic(o) + '</button>').join('') + '</div></div>').join('') + '</div>' : '') +
      (mods.length ? '<div class="rp-mods">' + mods.map(r => r.set
          ? '<button class="rp-mod edit' + (r.empty ? ' empty' : '') + '" data-modpick="' + esc(x.id + '|' + r.ix + '|' + r.set + '|' + x.hash) + '" title="' + esc((r.empty ? 'Empty mod slot' : r.act.n + (r.act.desc ? ': ' + r.act.desc : '')) + '\nClick to change') + '">' + (r.empty ? '<span class="rp-plus">+</span>' : pic(r.act)) + '</button>'
          : '<span class="rp-mod" title="' + esc(r.act.n + (r.act.t ? ' (' + r.act.t + ')' : '') + (r.act.desc ? ': ' + r.act.desc : '')) + '">' + pic(r.act) + '</span>').join('') + '</div><div class="rp-modlist hidden"></div>' : '') +
      (perks.some(r => r.opts.length > 1) || mods.some(r => r.set) ? '<div class="rp-hint">' + (perks.length ? 'Click a perk on the right to switch to it. ' : '') + (mods.some(r => r.set) ? 'Click a mod to change it. ' : '') + 'Works in orbit, a social space, or offline.</div>' : '') + '</div>';
  }
  // switch a perk: InsertSocketPlugFree on the item's character (or the Pull-to one for vault items), then re-read the roll
  let swapping = false;
  document.addEventListener('click', async e => {
    const b = e.target.closest('[data-swap]'); if (!b || swapping) return;
    e.stopPropagation();
    const [id, ix, plug, hash] = b.dataset.swap.split('|'), box = b.closest('[data-rollbox]');
    swapping = true; b.classList.add('busy');
    try {
      const x = await readRoll(id, +hash);
      const cid = x.charId || (typeof selChar === 'function' && selChar()) || ((state.chars || [])[0] || {}).id;
      await bungieAction('/Destiny2/Actions/Items/InsertSocketPlugFree/', { plug: { socketIndex: +ix, socketArrayType: 0, plugItemHash: +plug }, itemId: id, characterId: cid, membershipType: state.acct.membershipType });
      rollCache.delete(id); if (profIC) delete profIC.sockets[id];
      const nx = await readRoll(id, +hash);
      if (box && box.isConnected) box.outerHTML = rollHtml(nx);
      if (rollFor && !rpop.classList.contains('hidden')) placeRoll(rollFor);
      toast('Switched to ' + ((nx.rows.find(r => r.ix === +ix) || {}).act || {}).n);
    } catch (err){ setStatus('Perk change failed: ' + err.message + '\nPerk changes only work in orbit, a social space, or offline.', true); b.classList.remove('busy'); }
    finally { swapping = false; }
  }, true);

  // ---- mods: options are the account's unlocked plugs for that socket's plug set (profilePlugSets / characterPlugSets,
  // returned with component 305 on the profile). Read once per page, refreshed after 10 minutes.
  let plugSetsJob = null, plugSetsAt = 0;
  function plugSets(){
    if (plugSetsJob && Date.now() - plugSetsAt < 600e3) return plugSetsJob;
    plugSetsAt = Date.now();
    plugSetsJob = bungie('/Destiny2/' + state.acct.membershipType + '/Profile/' + state.acct.membershipId + '/?components=305')
      .then(r => ({ prof: ((r.profilePlugSets || {}).data || {}).plugs || {}, chars: ((r.characterPlugSets || {}).data) || {} }));
    plugSetsJob.catch(() => { plugSetsJob = null; });
    return plugSetsJob;
  }
  document.addEventListener('click', async e => {
    const b = e.target.closest('[data-modpick]'); if (!b) return;
    e.stopPropagation();
    const box = b.closest('[data-rollbox]'), list = box && box.querySelector('.rp-modlist'); if (!list) return;
    if (list.dataset.for === b.dataset.modpick && !list.classList.contains('hidden')){ list.classList.add('hidden'); return; }
    const [id, ix, set, hash] = b.dataset.modpick.split('|');
    list.dataset.for = b.dataset.modpick; list.classList.remove('hidden'); list.innerHTML = '<div class="dim-lbl">Loading your mods…</div>';
    box.querySelectorAll('.rp-mod.edit').forEach(x => x.classList.toggle('on', x === b));
    try {
      const x = await readRoll(id, +hash), ps = await plugSets();
      const cid = x.charId || (typeof selChar === 'function' && selChar()) || ((state.chars || [])[0] || {}).id;
      const raw = (ps.prof[set] || []).concat(((ps.chars[cid] || {}).plugs || {})[set] || []).filter(o => o.canInsert !== false && o.enabled !== false);
      const hashes = [...new Set(raw.map(o => o.plugItemHash))];
      const defs = hashes.length ? await entMany('DestinyInventoryItemDefinition', hashes) : {};
      const cur = (x.rows.find(r => r.ix === +ix) || {}).act || {};
      const opts = hashes.map(h => { const d = defs[h] || {}, dp = d.displayProperties || {}; return { h, n: dp.name || '', i: dp.icon || '', desc: dp.description || '', cost: (((d.plug || {}).energyCost) || {}).energyCost, t: d.itemTypeDisplayName || '' }; })
        .filter(o => o.n && !/^Deprecated/i.test(o.n)).sort((a, b) => (/^Empty /i.test(a.n) ? -1 : /^Empty /i.test(b.n) ? 1 : a.n.localeCompare(b.n)));
      if (!opts.length){ list.innerHTML = '<div class="dim-lbl">No unlocked mods fit this slot.</div>'; return; }
      const draw = q => { const w = q.trim().toLowerCase();
        list.querySelector('.rp-modopts').innerHTML = opts.filter(o => !w || (o.n + ' ' + o.desc + ' ' + o.t).toLowerCase().includes(w)).map(o =>
          '<button class="rp-modopt' + (o.h === cur.h ? ' cur' : '') + '" data-modset="' + esc(id + '|' + ix + '|' + o.h + '|' + hash) + '" title="' + esc(o.desc) + '">' + (o.i ? '<img decoding="async" src="' + img(o.i) + '" alt="">' : '<span class="rp-noimg"></span>') +
          '<span><b>' + esc(o.n) + '</b><small>' + esc([o.t, o.cost != null ? o.cost + ' energy' : ''].filter(Boolean).join(' · ')) + '</small></span></button>').join('') || '<div class="dim-lbl">No match.</div>'; };
      list.innerHTML = '<input type="search" class="rp-modq" placeholder="Filter mods" autocomplete="off"><div class="rp-modopts"></div>';
      draw(''); list.querySelector('.rp-modq').oninput = ev => draw(ev.target.value);
      if (rollFor && !rpop.classList.contains('hidden')) placeRoll(rollFor);
    } catch (err){ list.innerHTML = '<div class="dim-lbl">' + esc(err.message) + '</div>'; }
  }, true);
  document.addEventListener('click', async e => {
    const b = e.target.closest('[data-modset]'); if (!b || swapping) return;
    e.stopPropagation();
    const [id, ix, plug, hash] = b.dataset.modset.split('|'), box = b.closest('[data-rollbox]');
    swapping = true; b.classList.add('busy');
    try {
      const x = await readRoll(id, +hash);
      const cid = x.charId || (typeof selChar === 'function' && selChar()) || ((state.chars || [])[0] || {}).id;
      await bungieAction('/Destiny2/Actions/Items/InsertSocketPlugFree/', { plug: { socketIndex: +ix, socketArrayType: 0, plugItemHash: +plug }, itemId: id, characterId: cid, membershipType: state.acct.membershipType });
      rollCache.delete(id); if (profIC) delete profIC.sockets[id];
      const nx = await readRoll(id, +hash);
      if (box && box.isConnected) box.outerHTML = rollHtml(nx);
      if (rollFor && !rpop.classList.contains('hidden')) placeRoll(rollFor);
      toast('Mod changed: ' + (((nx.rows.find(r => r.ix === +ix) || {}).act || {}).n || 'done'));
    } catch (err){ b.classList.remove('busy'); setStatus('Mod change failed: ' + err.message + (/energy/i.test(err.message) ? '' : '\nMods change only in orbit, a social space, or offline, and the armor needs enough energy.'), true); }
    finally { swapping = false; }
  }, true);

  let rollFor = null, hoverT = null;
  function placeRoll(anchor){
    const r = anchor.getBoundingClientRect(), w = rpop.offsetWidth || 320, h = rpop.offsetHeight || 200;
    const right = window.innerWidth - (parseInt(getComputedStyle(document.body).getPropertyValue('--pinw')) || 0);   // keep clear of the pinned Activity panel
    let x = r.right + 10; if (x + w > right - 8) x = Math.max(8, r.left - w - 10);
    let y = Math.min(window.innerHeight - h - 8, Math.max(8, r.top));
    if (window.innerWidth < 640){ x = 8; y = Math.max(8, window.innerHeight - h - 8); }
    rpop.style.left = x + 'px'; rpop.style.top = y + 'px';
  }
  async function showRoll(el){
    const id = el.dataset.roll, hash = +el.dataset.rh; if (!id) return;
    rollFor = el;
    rpop.innerHTML = '<div class="dim-lbl">Reading roll…</div>'; rpop.classList.remove('hidden'); placeRoll(el);
    try { const x = await readRoll(id, hash); if (rollFor !== el) return; rpop.innerHTML = rollHtml(x); placeRoll(el); }
    catch (e){ if (rollFor === el){ rpop.innerHTML = '<div class="dim-lbl">' + esc(e.message || 'Could not read this roll.') + '</div>'; placeRoll(el); } }
  }
  function hideRoll(){ rollFor = null; rpop.classList.add('hidden'); }
  window.rollHtmlFor = async (id, hash) => rollHtml(await readRoll(id, hash));
  const fineHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (fineHover){
    document.addEventListener('mouseover', e => { const el = e.target.closest('[data-roll]'); if (!el || el === rollFor || e.target.closest('button, a')) return; clearTimeout(hoverT); if (el.dataset.roll) readRoll(el.dataset.roll, +el.dataset.rh).catch(() => {}); hoverT = setTimeout(() => showRoll(el), 140); });
    // a short grace period so the pointer can travel from the item into the card (to click a perk)
    let hideT = null;
    document.addEventListener('mouseout', e => { const el = e.target.closest('[data-roll]'); if (!el || (e.relatedTarget && el.contains(e.relatedTarget))) return; clearTimeout(hoverT);
      if (rollFor === el){ clearTimeout(hideT); hideT = setTimeout(() => { if (rollFor === el && !rpop.matches(':hover')) hideRoll(); }, 300); } });
    rpop.addEventListener('mouseenter', () => clearTimeout(hideT));
    rpop.addEventListener('mouseleave', () => { clearTimeout(hideT); hideT = setTimeout(() => { if (!rpop.matches(':hover') && !(rollFor && rollFor.matches(':hover'))) hideRoll(); }, 300); });
  }
  // tap or click (phones, or to pin it): toggles; clicks on buttons inside the row keep doing their own thing
  document.addEventListener('click', e => {
    if (e.target.closest('#rollPop')) return;
    const el = e.target.closest('[data-roll]');
    if (el && !e.target.closest('button, a')){ if (rollFor === el && !fineHover) hideRoll(); else showRoll(el); return; }
    if (rollFor) hideRoll();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && rollFor) hideRoll(); });
  window.addEventListener('scroll', () => { if (rollFor) hideRoll(); }, { passive: true, capture: true });

  pmButton();
  // the "Signed in until" text is hidden to save header room: show it on the Sign out button instead
  (function authTip(){ const a = $('authStatus'), b = $('btnAuth'); if (!a || !b) return;
    const sync = () => { b.title = a.textContent ? a.textContent + '. Click to sign out.' : 'Sign in with your Bungie account'; };
    new MutationObserver(sync).observe(a, { childList: true, characterData: true, subtree: true }); sync(); })();

  // status line and toasts float in the bottom-right corner instead of pushing the page down
  (function notices(){
    const st = $('status'); if (!st) return;
    const stack = document.createElement('div'); stack.id = 'noticeStack'; document.body.appendChild(stack);
    let t = document.querySelector('.toast');
    if (!t){ t = document.createElement('div'); t.className = 'toast'; }
    stack.appendChild(t);            // toast() finds this one and reuses it
    const box = document.createElement('div'); box.className = 'statusbox';
    const x = document.createElement('button'); x.className = 'stclose'; x.type = 'button'; x.title = 'Dismiss'; x.textContent = '×';
    box.appendChild(st);             // same #status element and setStatus(); the × sits beside it so the text stays clean
    box.appendChild(x);
    stack.appendChild(box);
    let timer = 0;
    const show = () => {
      clearTimeout(timer);
      const has = st.textContent.trim().length > 0;
      box.classList.toggle('live', has);
      box.classList.toggle('err', st.classList.contains('err'));
      if (has && !st.classList.contains('err')) timer = setTimeout(() => box.classList.remove('live'), 6000);   // errors stay until dismissed
    };
    x.onclick = () => { clearTimeout(timer); box.classList.remove('live'); };
    new MutationObserver(show).observe(st, { childList: true, characterData: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    show();
  })();

  // card tag menus (Weapons, Armor): one open at a time, and a click elsewhere closes it
  document.addEventListener('click', e => { document.querySelectorAll('details.tagpop[open]').forEach(d => { if (!d.contains(e.target)) d.open = false; }); });
  document.addEventListener('toggle', e => { if (e.target.matches && e.target.matches('details.tagpop') && e.target.open) document.querySelectorAll('details.tagpop[open]').forEach(d => { if (d !== e.target) d.open = false; }); }, true);
})();
