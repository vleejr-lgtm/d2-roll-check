/* Shared helpers for every page (loaded in <head> after rating.js, before the page script).
   One copy instead of seven: Bungie requests (bungie, bungieAction with throttle retry), the IndexedDB cache,
   manifest lookups (ent, entMany), moving items (transfer, pullFromPostmaster, pullTo, setLock), notices
   (setStatus, toast), the Pull-to select (fillCharSel), the signed-in account (getAccount) and the sign-in
   renewal (autoRenew). They use each page's own globals at call time: $, ls, auth, state, sleep, selChar, CLASS,
   PAGE. A page must NOT declare a function or top-level const/let with these names again. */
const entMem = new Map();
function setStatus(msg, err){ const s = $('status'); s.textContent = msg; s.className = err ? 'err' : ''; }
function toast(msg){
  let t = document.querySelector('.toast');
  if (!t){ t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2500);
}
async function copyText(text, msg){ try { await navigator.clipboard.writeText(text); toast(msg || 'Copied'); } catch { prompt('Copy this:', text); } }
let idbConn = null;
function idb(){ if (idbConn) return idbConn; idbConn = new Promise((res, rej) => { const r = indexedDB.open('d2rollcheck', 1); r.onupgradeneeded = () => r.result.createObjectStore('kv'); r.onsuccess = () => { const db = r.result; db.onversionchange = () => { db.close(); idbConn = null; }; db.onclose = () => { idbConn = null; }; res(db); }; r.onerror = () => { idbConn = null; rej(r.error); }; }); return idbConn; }
async function cacheGet(k){ try { const db = await idb(); return await new Promise(res => { const q = db.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result); q.onerror = () => res(undefined); }); } catch { return undefined; } }
async function cacheSet(k, v){ try { const db = await idb(); await new Promise(res => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, k); t.oncomplete = res; t.onerror = res; }); } catch {} }
async function net(url, what, opts){
  try { return await fetch(url, opts); }
  catch (e){ console.error('Fetch failed for', what, url, e); throw new Error('Could not download ' + what + '.\nURL: ' + url + '\nUsually an ad blocker, browser shield or firewall. Press F12, Console tab, for the exact reason.'); }
}
async function bungie(path, body, plainBody){
  const key = ls.get('apiKey');
  if (!key) throw new Error('Add your Bungie API key in Settings on the Weapons page first.');
  const headers = { 'X-API-Key': key };
  if (body && !plainBody) headers['Content-Type'] = 'application/json';
  if (auth.valid()) headers.Authorization = 'Bearer ' + auth.get().token;
  const r = await net('https://www.bungie.net/Platform' + path, 'Bungie API (' + path.split('/').slice(0, 3).join('/') + ')', { method: body ? 'POST' : 'GET', headers, cache: 'no-store', body: body ? JSON.stringify(body) : undefined });
  let j; try { j = await r.json(); } catch { throw new Error('Bungie API returned HTTP ' + r.status + '. Check that your API key Origin Header matches ' + location.origin); }
  if (j.ErrorCode !== 1) throw new Error(j.Message || j.ErrorStatus || 'Bungie API error');
  return j.Response;
}
async function bungieAction(path, body){
  if (!auth.valid()) throw new Error('Sign in with Bungie first (top right).');
  // Bungie throttles item moves when they come too fast: wait a moment and try again instead of failing
  // (lets multi-step moves run back to back with no fixed pauses)
  for (let n = 0; ; n++){
    try { return await bungie(path, body); }
    catch (e){
      if (/Could not download/.test(e.message)){ try { return await bungie(path, body, true); } catch (e2){ e = e2; } }
      if (n < 3 && /thrott|too many|too quickly|try again/i.test(e.message || '')){ await sleep(350 * (n + 1)); continue; }
      throw e;
    }
  }
}
async function ent(type, hash){
  const k = type + ':' + hash;
  if (entMem.has(k)) return entMem.get(k);
  const p = (async () => {
    const c = await cacheGet('ent:' + k);
    if (c && c.v === state.manVer) return c.d;
    let d, lastErr;
    for (const wait of [0, 1500, 4000]){
      if (wait) await sleep(wait);
      try { d = await bungie('/Destiny2/Manifest/' + type + '/' + hash + '/'); lastErr = null; break; }
      catch (e){ lastErr = e; if (!/origin|throttl|busy|unavailable|try again|Could not download/i.test(e.message)) break; }
    }
    if (lastErr) throw lastErr;
    await cacheSet('ent:' + k, { v: state.manVer, d });
    return d;
  })();
  entMem.set(k, p);
  try { return await p; } catch (e){ entMem.delete(k); throw e; }
}
async function entMany(type, hashes){
  const out = {}, list = [...new Set(hashes.filter(Boolean))];
  for (let i = 0; i < list.length; i += 8) await Promise.all(list.slice(i, i + 8).map(async h => { try { out[h] = await ent(type, h); } catch (e){ console.warn(type, h, e.message); } }));
  return out;
}
function isGoneError(e){ return /item requested was not found|DestinyItemNotFound|item not found/i.test((e && e.message) || ''); }
function fillCharSel(p){
  const acts = (p.characterActivities && p.characterActivities.data) || {};
  const live = state.chars.find(c => acts[c.id] && acts[c.id].currentActivityHash);
  state.activeChar = (live || state.chars[0] || {}).id;
  const a = state.chars.find(c => c.id === state.activeChar);
  const saved = ls.get('pullChar2') || 'auto';
  $('charSel').innerHTML = '<option value="auto">Pull to: Auto (' + esc(a ? a.name : '?') + (live ? ', playing now' : ', last played') + ')</option>' +
    state.chars.map(c => '<option value="' + esc(c.id) + '">Pull to: ' + esc(c.name) + (c.light ? ' ' + c.light : '') + '</option>').join('');
  $('charSel').value = (saved !== 'auto' && state.chars.some(c => c.id === saved)) ? saved : 'auto';
}
async function setLock(i, v){ await bungieAction('/Destiny2/Actions/Items/SetLockState/', { state: v, itemId: i.id, characterId: i.charId || selChar(), membershipType: state.acct.membershipType }); i.locked = v; }
async function transfer(i, toVault, charId){
  const go = () => bungieAction('/Destiny2/Actions/Items/TransferItem/', { itemReferenceHash: i.hash, stackSize: 1, transferToVault: toVault, itemId: i.id, characterId: charId, membershipType: state.acct.membershipType });
  if (toVault){ await go(); if (typeof pmLeft === 'function') pmLeft(charId, i.id); return; }
  // to a character: when that slot is full, stream.js first moves the lowest rarity, lowest power unlocked item there to the vault
  const room = async force => { if (typeof pmEnsureRoom !== 'function') return {}; const r = await pmEnsureRoom(charId, i.hash, true, force);
    if (r.err) throw new Error('No room for ' + i.name + ': ' + r.err + '.'); if (r.moved){ toast('Moved ' + r.moved + ' to the vault to make room'); await sleep(300); } return r; };
  await room(false);
  try { await go(); }
  catch (e){ if (typeof pmIsNoRoom !== 'function' || !pmIsNoRoom(e) || ls.get('pmMakeRoom') === '0') throw e; await room(true); await go(); }
  if (typeof pmLanded === 'function') pmLanded(charId, { id: i.id, hash: i.hash, qty: 1 });
}
async function pullFromPostmaster(i){
  // stream.js (Postmaster panel) frees a slot first by moving an unlocked item to the vault when the slot is full
  const go = () => bungieAction('/Destiny2/Actions/Items/PullFromPostmaster/', { itemReferenceHash: i.hash, stackSize: i.qty || 1, itemId: i.id, characterId: i.charId, membershipType: state.acct.membershipType });
  const room = async force => { if (typeof pmEnsureRoom !== 'function') return {}; const r = await pmEnsureRoom(i.charId, i.hash, !!i.id && i.id !== '0', force);
    if (r.err) throw new Error(i.name + ' stayed in the postmaster: ' + r.err + '.'); if (r.moved){ toast('Moved ' + r.moved + ' to the vault to make room'); await sleep(300); } return r; };
  await room(false);
  try { await go(); }
  catch (e){ if (typeof pmIsNoRoom !== 'function' || !pmIsNoRoom(e) || ls.get('pmMakeRoom') === '0') throw e; await room(true); await go(); }
  if (typeof pmLanded === 'function') pmLanded(i.charId, { id: i.id, hash: i.hash, qty: i.qty || 1 });
  i.postmaster = false; i.loc = (state.chars.find(c => c.id === i.charId) || {}).name || 'Character';
}
async function pullTo(i, target){
  if (i.postmaster){ await pullFromPostmaster(i); }
  if (i.charId === target) return;
  if (i.equipped) throw new Error(i.name + ' is equipped. Unequip it in game first.');
  if (i.charId){
    // free a slot on the target (if it's full) while the item travels to the vault: two Bungie calls at once, not one after the other
    const pre = typeof pmEnsureRoom === 'function' && ls.get('pmMakeRoom') !== '0' ? pmEnsureRoom(target, i.hash, true, false).then(r => { if (r && r.moved) toast('Moved ' + r.moved + ' to the vault to make room'); }).catch(() => {}) : null;
    await transfer(i, true, i.charId); i.charId = null; i.loc = 'Vault';
    if (pre) await pre;
  }
  await transfer(i, false, target); i.charId = target; i.loc = (state.chars.find(c => c.id === target) || {}).name || 'Character';
}
async function getAccount(){
  if (state.acct) return state.acct;
  const me = await (window.myMemberships ? myMemberships(bungie) : bungie('/User/GetMembershipsForCurrentUser/'));
  const ms = me.destinyMemberships || [];
  const a = ms.find(x => x.membershipId === me.primaryMembershipId) || ms.find(x => x.crossSaveOverride && x.membershipType === x.crossSaveOverride) || ms[0];
  if (!a) throw new Error('No Destiny account found on your signed-in Bungie account.');
  state.acct = { membershipType: a.membershipType, membershipId: a.membershipId };
  return state.acct;
}
/* Optional sign-in worker (worker/token-worker.js). When config.js has tokenProxy, sign-in codes are exchanged
   through it and the page keeps Bungie's refresh token (90 days), so renewal is a quiet background call instead of a
   trip through bungie.net every hour. Without tokenProxy everything works as before. */
const tokenProxy = () => ((window.D2RC_CONFIG || {}).tokenProxy || '').replace(/\/+$/, '');
function saveTokens(j){
  const old = auth.get() || {};
  auth.set({ token: j.access_token, exp: Date.now() + (j.expires_in || 3600) * 1000, bnetId: j.membership_id || old.bnetId,
    refresh: j.refresh_token || old.refresh || null, rexp: j.refresh_token ? Date.now() + (j.refresh_expires_in || 7776000) * 1000 : (old.rexp || 0) });
}
async function exchangeCode(code){
  const px = tokenProxy();
  const r = px
    ? await net(px + '/token', 'the sign-in worker', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) })
    : await net('https://www.bungie.net/Platform/App/OAuth/Token/', 'Bungie sign-in token', { method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-API-Key': ls.get('apiKey') || '' },
        body: 'grant_type=authorization_code&code=' + encodeURIComponent(code) + '&client_id=' + encodeURIComponent(ls.get('clientId') || '') });
  const j = await r.json().catch(() => ({}));
  if (!j.access_token) throw new Error('Bungie sign-in failed: ' + (j.error_description || j.error || ('HTTP ' + r.status)));
  saveTokens(j);
  return j;
}
let refreshing = null;
function refreshQuietly(){
  if (refreshing) return refreshing;
  const px = tokenProxy(), a = auth.get();
  if (!px || !a || !a.refresh || !(a.rexp > Date.now() + 60e3)) return Promise.resolve(false);
  refreshing = (async () => {
    try {
      const r = await fetch(px + '/refresh', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: a.refresh }) });
      const j = await r.json().catch(() => ({}));
      if (!j.access_token){ const b = auth.get(); if (b){ b.refresh = null; auth.set(b); } return false; }   // fall back to the normal renewal next time
      saveTokens(j); if (typeof updateAuthUi === 'function') updateAuthUi();
      return true;
    } catch { return false; } finally { refreshing = null; }
  })();
  return refreshing;
}
function autoRenew(){
  { const a = auth.get();   // with the sign-in worker: renew quietly a few minutes early, no page change
    if (a && a.refresh && tokenProxy() && a.exp - Date.now() < 5 * 60e3 && !refreshing){ refreshQuietly(); return false; } }
  if (ls.get('authAuto') !== '1' || location.protocol !== 'https:' || document.hidden) return false;
  if (/[?&]code=/.test(location.search)) return false;           // finishing a sign-in right now
  const a = auth.get(); if (!a || !a.token) return false;
  const expired = !auth.valid(), idle = Date.now() - lastInput > 60e3;
  if (!expired && !(a.exp - Date.now() < 4 * 60e3 && idle)) return false;   // renew early only when nobody is clicking
  if (state.scanning) return false;
  let last = 0; try { last = +sessionStorage.getItem('renewAt') || 0; } catch {}
  if (Date.now() - last < 3 * 60e3) return false;
  const cid = ls.get('clientId'); if (!cid) return false;
  const st = Math.random().toString(36).slice(2) + Date.now().toString(36);
  const page = (location.pathname.split('/').pop() || 'index.html') + (/^#[a-z]+$/.test(location.hash) ? location.hash : '');
  try { sessionStorage.setItem('renewAt', String(Date.now())); sessionStorage.setItem('oauthState', st); sessionStorage.setItem('returnTo', page); } catch {}
  setStatus('Renewing your Bungie sign-in...');
  location.href = 'https://www.bungie.net/en/OAuth/Authorize?client_id=' + encodeURIComponent(cid) + '&response_type=code&state=' + st;
  return true;
}

/* ---- In-game style Inventory section (Character and Vault pages) ----
   Every non-equippable storage area the profile holds, like the game's inventory screen: Engrams (per character),
   Consumables, Modifications and the rest. Bucket names and sizes come from DestinyInventoryBucketDefinition
   (cached); Bungie leaves some unnamed, those are named after what they hold. Pursuits, quests, the vault itself and
   the postmaster are left out (they have their own views). */
const INV_SKIP = new Set([138197802, 215593132, 1345459588, 1801258597,   // vault, postmaster, pursuits, quests
  1498876634, 2465295065, 953998645, 3448274439, 3551918588, 14239492, 20886954, 1585787867,   // weapon and armor slots
  4023194814, 3284755031, 4274335291, 2025709351, 284967655, 1506418338, 4292445962]);   // ghost, subclass, emblem, sparrow, ship, artifact, clan banner
const INV_NAME = { 375726501: 'Engrams', 1469714392: 'Consumables', 3313201758: 'Modifications' };
async function readInventory(p, charIds){
  const groups = new Map();
  const add = (it, owner) => {
    if (INV_SKIP.has(it.bucketHash)) return;
    const k = it.bucketHash + '|' + (owner || '');
    let g = groups.get(k); if (!g){ g = { h: it.bucketHash, owner, items: [] }; groups.set(k, g); }
    g.items.push(it);
  };
  for (const it of ((p.profileInventory || {}).data || {}).items || []) add(it, '');
  const inv = (p.characterInventories || {}).data || {};
  for (const cid of charIds || Object.keys(inv)) for (const it of (inv[cid] || {}).items || []) add(it, cid);
  let defs = {};
  try { defs = await entMany('DestinyInventoryBucketDefinition', [...new Set([...groups.values()].map(g => g.h))]); } catch {}
  const typeName = g => { const t = {}; for (const it of g.items){ const n = ((state.defs || {})[it.itemHash] || {}).t; if (n) t[n] = (t[n] || 0) + 1; } const top = Object.entries(t).sort((a, b) => b[1] - a[1])[0]; return top ? top[0] : ''; };
  const out = [];
  for (const g of groups.values()){
    const d = defs[g.h] || {};
    if (d.category === 3 || d.category === 0) continue;   // equippable slots and invisible buckets
    const name = INV_NAME[g.h] || (d.displayProperties || {}).name || typeName(g) || 'Other storage';
    out.push({ h: g.h, owner: g.owner, name, cap: d.itemCount || 0, items: g.items.map(it => { const x = (state.defs || {})[it.itemHash] || {}; return { h: it.itemHash, id: it.itemInstanceId || '', n: x.n || 'Item', i: x.i || '', q: it.quantity || 1, rar: x.tier || 0 }; }) });
  }
  const order = h => h === 375726501 ? 0 : h === 1469714392 ? 1 : h === 3313201758 ? 2 : 3;
  out.sort((a, b) => order(a.h) - order(b.h) || a.name.localeCompare(b.name));
  return out;
}
function inventoryHtml(sections, charName, extra){
  if (!sections || !sections.length) return '';
  const img = p => p ? 'https://www.bungie.net' + esc(p) : '';
  const box = it => '<span class="inv-it r' + it.rar + '"' + (it.id ? ' data-roll="' + esc(it.id) + '" data-rh="' + it.h + '"' : '') + ' title="' + esc(it.n + (it.q > 1 ? ' ×' + it.q.toLocaleString() : '')) + '">' +
    (it.i ? '<img decoding="async" loading="lazy" src="' + img(it.i) + '" alt="">' : '') + (it.q > 1 ? '<b>' + it.q.toLocaleString() + '</b>' : '') + '</span>';
  return '<div class="panel invpanel"><div class="cslot-lbl inv-title">Inventory' + (extra || '') + '</div><div class="invgrid">' + sections.map(s => {
    const used = s.items.length, full = s.cap && used >= s.cap, warn = s.cap && used / s.cap >= .85;
    const empties = s.cap && s.cap <= 21 ? Math.max(0, s.cap - used) : 0;
    return '<div class="invsec' + (full ? ' full' : warn ? ' warn' : '') + '"><div class="invhead"><span>' + esc(s.name) + (s.owner && charName ? ' <small>' + esc(charName(s.owner)) + '</small>' : '') + '</span><b>' + used + (s.cap ? '/' + s.cap : '') + '</b></div>' +
      '<div class="invrow">' + s.items.slice().sort((a, b) => b.rar - a.rar || b.q - a.q).map(box).join('') + '<span class="inv-it empty"></span>'.repeat(empties) + '</div></div>';
  }).join('') + '</div></div>';
}

/* Installable app: register the service worker (https only, never inside the hidden labeler frames). */
if ('serviceWorker' in navigator && location.protocol === 'https:' && window === window.top){
  window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js?v=__BUILD__').catch(e => console.warn('service worker', e)); });
}
