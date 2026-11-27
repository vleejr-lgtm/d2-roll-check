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

  window.trackDrops = function(p){
    try { pmCapture(p); } catch (e){ console.warn('postmaster', e); }
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
    if (fresh.length > 40) evs.push({ t: now, kind: 'info', page: PAGE, text: '+' + (fresh.length - 40) + ' more new items not listed' });
    for (const kind of KINDS){
      if (!known.kinds[kind]) continue;
      const gone = Object.keys(known.ids).filter(id => known.ids[id][1] === kind && !state.gear.has(id)).map(id => known.ids[id][0]);
      if (gone.length) evs.push({ t: now, kind: 'gone', page: kind, names: gone.slice(0, 30), count: gone.length });
    }
    if (fresh.length && !$('streamMute').checked){
      const f = fresh[0], inf = ownInfo(f.kind === PAGE ? byId(f.id) : null);
      toast(fresh.length === 1 ? 'New drop: ' + f.name + (inf ? ' (' + inf.label + ')' : '') + (f.postmaster ? ' in your postmaster' : '') : fresh.length + ' new drops. Open 📡 Activity to see them.');
    }
    ls.set('known:all', JSON.stringify({ kinds: { weapons: true, armor: true }, ids: Object.fromEntries(gear.map(g => [g.id, [g.name, g.kind]])) }));
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
    try {
      if (act === 'lock'){ await setLock(g, !g.locked); toast((g.locked ? 'Locked ' : 'Unlocked ') + g.name); }
      else {
        let target = selChar();
        if (g.kind === 'armor'){   // class armor can only go to a character of that class
          const d = await ent('DestinyInventoryItemDefinition', g.hash);
          const want = d && d.classType < 3 ? CLS[d.classType] : '';
          const cur = state.chars.find(c => c.id === target);
          if (want && (!cur || cur.name !== want)){ const m = state.chars.find(c => c.name === want); if (!m) throw new Error('You have no ' + want + ' to pull it to.'); target = m.id; }
        }
        await pullTo(g, target); toast('Pulled ' + g.name + ' to ' + g.loc);
      }
    } catch (e){
      if (isGoneError(e)){ state.gear.delete(g.id); toast(g.name + ' is already gone.'); }
      else setStatus(g.name + ': ' + e.message, true);
    } finally { btn.disabled = false; renderStream(); }
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
      const locTxt = rec ? (rec.postmaster ? '📬 ' : '') + esc(rec.loc) : gear ? 'No longer in your inventory' : esc(e.loc || '');
      const details = own ? '<button data-sact="open" data-sid="' + esc(e.id) + '">Details</button>'
        : PAGEOF[e.page] ? '<a href="' + PAGEOF[e.page] + '#open=' + esc(e.id) + '">' + (e.v === 'new' ? 'Rate it on the ' : 'Details on the ') + PTITLE[e.page] + ' page</a>' : '';
      return '<div class="sev drop' + (e.t > seen ? ' unseen' : '') + '"><img src="' + (e.icon ? 'https://www.bungie.net' + esc(e.icon) : '') + '" alt="">' +
        '<div class="sb-body"><div class="sb-top"><b>' + esc(e.name) + '</b><span>' + kindTag + '<span class="sb sb-' + esc(e.v) + '">' + esc(e.label) + '</span></span></div>' +
        '<div class="dim-lbl">' + esc(e.extra || '') + '</div>' +
        '<div class="sloc' + (rec && rec.postmaster ? ' pm' : '') + '">' + locTxt + when + '</div>' +
        '<div class="sbtn">' + (rec ? '<button class="needauth" data-sact="pull" data-sid="' + esc(e.id) + '">' + (rec.postmaster ? '📬 Pull from postmaster' : 'Pull') + '</button>' +
          '<button class="needauth" data-sact="lock" data-sid="' + esc(e.id) + '">' + (rec.locked ? '🔒 Unlock' : '🔓 Lock') + '</button>' : '') + (rec || !gear ? details : '') + '</div>' +
        '</div></div>';
    }).join('') || '<div class="dim-lbl" style="padding:14px">Nothing yet. Scan, then new drops appear here as auto-refresh finds them.</div>';
    $('streamList').querySelectorAll('[data-sact]').forEach(b => b.onclick = () => {
      const id = b.dataset.sid, own = byId(id);
      if (own){ if (b.dataset.sact === 'open') streamOpen(own); else Promise.resolve(runAction(b.dataset.sact, id, b)).then(renderStream); return; }
      const g = state.gear && state.gear.get(id); if (g) actOther(b.dataset.sact, g, b);
    });
  }
  window.renderStream = renderStream;

  $('btnStream').onclick = () => { const s = $('stream'); s.classList.toggle('hidden'); if (!s.classList.contains('hidden')) renderStream(); ls.set('streamSeen', String(Date.now())); setTimeout(renderStream, 50); };
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
  window.addEventListener('storage', e => { if (e.key === 'stream') renderStream(); });
  renderStream();


  /* ---- Postmaster: every character's Lost Items, on every page ----
     Read from the same profile refresh (characterInventories, bucket 215593132). Pull one stack or everything for a
     character with PullFromPostmaster. The postmaster holds 21 items per character; past that, new drops are lost. */
  const PM_CAP = 21;
  let pm = null;                       // { at, chars: [{ id, name, items: [{ id, hash, qty }] }] }
  const pmNames = {};
  function pmCapture(p){
    const chars = (p.characters && p.characters.data) || {}, inv = (p.characterInventories && p.characterInventories.data) || {};
    if (!Object.keys(chars).length) return;
    pm = { at: Date.now(), chars: Object.values(chars).sort((a, b) => new Date(b.dateLastPlayed) - new Date(a.dateLastPlayed)).map(c => ({
      id: c.characterId, name: CLS[c.classType] || 'Character',
      items: ((inv[c.characterId] || {}).items || []).filter(it => it.bucketHash === PM).map(it => ({ id: it.itemInstanceId || '0', hash: it.itemHash, qty: it.quantity || 1 })) })) };
    pmButton(); if (!$('pmPanel').classList.contains('hidden')) pmRender();
  }
  const pmTotal = () => pm ? pm.chars.reduce((n, c) => n + c.items.length, 0) : 0;
  const pmFull = () => pm ? Math.max(0, ...pm.chars.map(c => c.items.length)) : 0;
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
    pmBtn.classList.toggle('hidden', !pm);
    pmBtn.classList.toggle('pmwarn', full >= PM_CAP - 3);
    pmBtn.innerHTML = '📬' + (n ? '<b class="scount' + (full >= PM_CAP - 3 ? ' pmhot' : '') + '">' + n + '</b>' : '');
    pmBtn.title = n ? n + ' item' + (n > 1 ? 's' : '') + ' in your postmaster' + (full >= PM_CAP - 3 ? '. Almost full: new drops will be lost past ' + PM_CAP + '.' : '') : 'Postmaster is empty';
  }
  // panel
  const panel = document.createElement('div');
  panel.id = 'pmPanel'; panel.className = 'stream pmpanel hidden';
  panel.innerHTML = '<div class="stream-head"><b>📬 Postmaster</b><span style="flex:1"></span><button class="ghost" id="pmRefresh" title="Re-read from Bungie">↻</button><button class="ghost" id="pmClose">✕</button></div>' +
    '<div class="dim-lbl" style="padding:0 14px 8px">Lost items on each character. Each postmaster holds ' + PM_CAP + '; anything past that is gone. Pulling needs room in that character\'s inventory.</div><div id="pmList"></div>';
  document.body.appendChild(panel);
  pmBtn.onclick = () => { panel.classList.toggle('hidden'); if (!panel.classList.contains('hidden')){ $('stream').classList.add('hidden'); pmRender(); } };
  $('pmClose').onclick = () => panel.classList.add('hidden');
  $('pmRefresh').onclick = () => { if (typeof scan === 'function') scan({ silent: true }); };
  const img = p => p ? 'https://www.bungie.net' + esc(p) : '';
  function pmRender(){
    const list = $('pmList');
    if (!pm){ list.innerHTML = '<div class="sev info">Sign in and load the page to read your postmaster.</div>'; return; }
    list.innerHTML = pm.chars.map(c => {
      const n = c.items.length, hot = n >= PM_CAP - 3;
      return '<div class="pmchar"><div class="pmhead"><b>' + esc(c.name) + '</b><span class="pmcount' + (hot ? ' hot' : '') + '">' + n + ' / ' + PM_CAP + '</span><span style="flex:1"></span>' +
        (n ? '<button class="ghost pmall" data-pmall="' + esc(c.id) + '">Pull all</button>' : '') + '</div>' +
        (n ? c.items.map((it, ix) => { const d = pmDef(it.hash);
          return '<div class="pmrow">' + (d.i ? '<img src="' + img(d.i) + '" alt="">' : '<span class="pmnoimg"></span>') + '<span class="pmname">' + esc(d.n) + (it.qty > 1 ? ' <span class="dim-lbl">×' + it.qty + '</span>' : '') + '</span>' +
            '<button class="ghost pmone" data-pmc="' + esc(c.id) + '" data-pmi="' + ix + '">Pull</button></div>'; }).join('')
          : '<div class="dim-lbl pmempty">Empty</div>') + '</div>';
    }).join('') + '<div class="dim-lbl" style="padding:6px 4px">Read ' + new Date(pm.at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) + '</div>';
    list.querySelectorAll('[data-pmi]').forEach(b => b.onclick = () => pmPull(b.dataset.pmc, [c => c.items[+b.dataset.pmi]], b));
    list.querySelectorAll('[data-pmall]').forEach(b => b.onclick = () => pmPull(b.dataset.pmall, null, b));
  }
  let pmBusy = false;
  async function pmPull(cid, pick, btn){
    if (pmBusy) return;
    if (!state.acct || !auth.valid()){ setStatus('Sign in with Bungie (top right) to pull from the postmaster.', true); return; }
    const ch = pm.chars.find(c => c.id === cid); if (!ch) return;
    const items = pick ? pick.map(f => f(ch)).filter(Boolean) : ch.items.slice();
    pmBusy = true; btn.disabled = true; btn.textContent = '…';
    let ok = 0; const fails = [];
    for (const it of items){
      try {
        await bungieAction('/Destiny2/Actions/Items/PullFromPostmaster/', { itemReferenceHash: it.hash, stackSize: it.qty, itemId: it.id, characterId: cid, membershipType: state.acct.membershipType });
        ch.items = ch.items.filter(x => x !== it); ok++;
        const g = it.id !== '0' && state.gear && state.gear.get(it.id); if (g){ g.postmaster = false; g.loc = ch.name; }
        const own = it.id !== '0' && typeof byId === 'function' ? byId(it.id) : null; if (own){ own.postmaster = false; own.loc = ch.name; }
      } catch (e){
        const m = e.message || '';
        fails.push(pmDef(it.hash).n + ': ' + (/NoRoom|no room|full/i.test(m) ? 'no room on your ' + ch.name : /cannot|not allowed|NotTransferrable/i.test(m) ? 'can\'t be pulled (pick it up in game)' : m));
        if (/NoRoom|no room|full/i.test(m)) break;   // the rest won't fit either
      }
      await new Promise(r => setTimeout(r, 250));
    }
    pmBusy = false; pmButton(); pmRender();
    if (ok) toast('Pulled ' + ok + ' item' + (ok > 1 ? 's' : '') + ' to your ' + ch.name);
    if (fails.length) setStatus('Some items stayed in the postmaster:\n' + fails.slice(0, 6).join('\n') + (fails.length > 6 ? '\n+' + (fails.length - 6) + ' more' : ''), true);
    if (ok && typeof render === 'function') try { render(); } catch {}
  }
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
