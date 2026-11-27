/* PvE vs PvP rating, shared by every page (loaded in <head>, before each page's own script).

   modeSplit() scores one weapon roll separately for PvE and PvP from the merged wishlists:
     best   how much of the closest recommended roll this copy can have (selected or selectable perks)
     combo  how much of a recommended trait pair it has (the part that matters most)
     full   how many recommended rolls it fully matches (more lists agreeing = more confidence)
     Aegis  endgame tier nudges the PvE score (S +8 ... F -10)
   overall = 50% best + 35% combo + 15% min(full/3, 1), plus the Aegis nudge, 0..100.
   A roll on a community trash list for that mode scores 0. No rolls for a mode = null (not rated).
   Untagged rolls count for both modes, only when the weapon has no tagged rolls.

   Compact form (stored in localStorage verdicts:weapons so every page can draw it):
     { pve: [overall, combo%, best%, fullMatches, trashListed] | null, pvp: [...] | null }

   modeGraph() draws it: a five colour bar per mode, a letter grade, Keep / Maybe / Trash for that mode,
   and a one line lean ("Better for PvP"). */
(function(){
  const norm = s => (s || '').toLowerCase().replace(/\benhanced\b/g, '').replace(/[^a-z0-9]/g, '');
  const AEGIS = { S: 8, A: 5, B: 2, C: 0, D: -4, E: -7, F: -10 };

  function modeSplit(hash, have, nameOf, typeOf, wl){
    if (!wl || !wl.good) return null;
    const owned = h => have.has(norm(nameOf(h)));
    const isTrait = h => /trait/i.test(typeOf(h) || '');
    const good = wl.good.get(hash) || [], bad = (wl.trash && wl.trash.get(hash)) || [];
    let aegis = ''; for (const e of good) if (e.at){ aegis = e.at; break; }
    const out = {};
    // untagged rolls only count when a weapon has no tagged ones (same rule as the detail view's rollsFor)
    const tagged = good.some(e => e.m);
    for (const m of ['pve', 'pvp']){
      const fits = e => (!e.m && !tagged) || e.m === 'both' || e.m === m;
      if (bad.filter(fits).some(e => !e.p.length || e.p.every(owned))){ out[m] = [0, 0, 0, 0, 1]; continue; }
      const rolls = good.filter(fits);
      if (!rolls.length){ out[m] = null; continue; }
      let best = 0, full = 0, combo = 0, seen = false;
      for (const e of rolls){
        const len = e.p.length;
        if (!len){ best = 1; full++; combo = 1; seen = true; continue; }   // whole weapon recommended
        const hit = e.p.filter(owned).length, f = hit / len;
        if (f > best) best = f;
        if (f === 1) full++;
        const ts = e.p.filter(isTrait);
        if (ts.length){ seen = true; const c = ts.filter(owned).length / ts.length; if (c > combo) combo = c; }
      }
      if (!seen) combo = best;
      let o = 100 * (0.5 * best + 0.35 * combo + 0.15 * Math.min(1, full / 3));
      if (m === 'pve' && aegis) o += AEGIS[aegis] || 0;
      out[m] = [Math.max(0, Math.min(100, Math.round(o))), Math.round(combo * 100), Math.round(best * 100), full, 0];
    }
    out.aegis = aegis;
    return out;
  }

  // what a whole weapon (no specific roll) is recommended for: rolls per mode and the most wanted traits
  function weaponModes(hash, nameOf, typeOf, wl){
    const good = (wl && wl.good && wl.good.get(hash)) || [];
    const res = { pve: { n: 0, traits: new Map() }, pvp: { n: 0, traits: new Map() }, aegis: '' };
    const tagged = good.some(e => e.m);
    for (const e of good){
      if (!e.m && tagged) continue;
      if (e.at && !res.aegis) res.aegis = e.at;
      for (const m of ['pve', 'pvp']){
        if (e.m && e.m !== 'both' && e.m !== m) continue;
        res[m].n++;
        for (const h of e.p) if (/trait/i.test(typeOf(h) || '')){ const n = nameOf(h); if (n) res[m].traits.set(n, (res[m].traits.get(n) || 0) + 1); }
      }
    }
    for (const m of ['pve', 'pvp']) res[m].top = [...res[m].traits].sort((a, b) => b[1] - a[1]).slice(0, 4).map(x => x[0]);
    return res;
  }

  const grade = o => o >= 88 ? 'S' : o >= 75 ? 'A' : o >= 60 ? 'B' : o >= 45 ? 'C' : o >= 30 ? 'D' : 'F';
  const call = s => !s ? ['none', 'No data'] : s[4] ? ['trash', 'Trash list'] : s[0] >= 70 ? ['keep', 'Keep'] : s[0] >= 45 ? ['maybe', 'Maybe'] : ['trash', 'Trash'];
  function lean(sp){
    const e = sp && sp.pve, v = sp && sp.pvp;
    if (!e && !v) return 'No community rolls for this weapon in either mode.';
    if (!v) return e[0] >= 70 ? 'Rated for PvE only. Keep it for PvE.' : e[0] >= 45 ? 'Rated for PvE only. Middle of the pack.' : 'Rated for PvE only, and this roll is weak there.';
    if (!e) return v[0] >= 70 ? 'Rated for PvP only. Keep it for PvP.' : v[0] >= 45 ? 'Rated for PvP only. Middle of the pack.' : 'Rated for PvP only, and this roll is weak there.';
    const d = e[0] - v[0];
    if (e[0] >= 70 && v[0] >= 70) return 'Strong in both. Keep it.';
    if (e[0] < 45 && v[0] < 45) return 'Weak in both modes. Safe to dismantle.';
    if (d >= 15) return 'Better for PvE' + (e[0] >= 70 ? '. Keep it for PvE.' : '.');
    if (d <= -15) return 'Better for PvP' + (v[0] >= 70 ? '. Keep it for PvP.' : '.');
    return 'About the same in both modes.';
  }
  // overall keep / trash from the better of the two modes
  function decide(sp){
    const e = sp && sp.pve, v = sp && sp.pvp;
    const se = e && !e[4] ? e[0] : e ? 0 : -1, sv = v && !v[4] ? v[0] : v ? 0 : -1;
    if (se < 0 && sv < 0) return { cls: 'none', text: 'Not rated', mode: '' };
    const m = se >= sv ? 'PvE' : 'PvP', s = Math.max(se, sv);
    if (se >= 70 && sv >= 70) return { cls: 'keep', text: 'Keep for both', mode: 'both' };
    return s >= 70 ? { cls: 'keep', text: 'Keep for ' + m, mode: m } : s >= 45 ? { cls: 'maybe', text: 'Maybe, best in ' + m, mode: m } : { cls: 'trash', text: 'Trash in both', mode: '' };
  }

  const h = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function row(label, s, compact){
    const [cls, word] = call(s);
    const g = s ? (s[4] ? 'F' : grade(s[0])) : '–';
    const pct = s ? s[0] : 0;
    const tip = !s ? 'No ' + label + ' rolls on your lists' : s[4] ? 'On a community trash list for ' + label
      : label + ' score ' + s[0] + '/100 · trait pair ' + s[1] + '% · closest roll ' + s[2] + '% · fully matches ' + s[3] + ' recommended roll' + (s[3] === 1 ? '' : 's');
    return '<div class="mg-row" title="' + h(tip) + '"><span class="mg-m">' + label + '</span>' +
      '<span class="mg-bar' + (s ? '' : ' off') + '"><u style="left:' + pct + '%"></u>' + (s ? '<em style="left:' + pct + '%"></em>' : '') + '</span>' +
      '<b class="mg-g g' + g + '">' + g + '</b><span class="mg-v ' + cls + '">' + word + '</span></div>' +
      (!compact && s && !s[4] ? '<div class="mg-sub"><span>Trait pair<i><b style="width:' + s[1] + '%"></b></i></span><span>Closest roll<i><b style="width:' + s[2] + '%"></b></i></span><span>' + s[3] + ' full match' + (s[3] === 1 ? '' : 'es') + '</span></div>' : '');
  }
  function modeGraph(sp, opts){
    opts = opts || {};
    if (!sp) return '';
    const d = decide(sp);
    return '<div class="mg' + (opts.compact ? ' compact' : '') + '">' +
      (opts.compact ? '' : '<div class="mg-head"><span>PvE vs PvP</span><span class="mg-call ' + d.cls + '">' + d.text + '</span></div>') +
      row('PvE', sp.pve, opts.compact) + row('PvP', sp.pvp, opts.compact) +
      (opts.compact ? '' : '<div class="mg-lean">' + h(lean(sp)) + (sp.aegis ? ' <span class="mg-aegis">Aegis ' + h(sp.aegis) + ' tier</span>' : '') + '</div>') + '</div>';
  }
  // short text for tiles and the Activity stream: "PvE A · PvP D"
  function modeShort(sp){
    if (!sp) return '';
    const p = (l, s) => s ? l + ' ' + (s[4] ? 'F' : grade(s[0])) : '';
    return [p('PvE', sp.pve), p('PvP', sp.pvp)].filter(Boolean).join(' · ');
  }
  // saved splits from the Weapons page scan (every page can read these by item instance id)
  // parsed once and kept for 3 s (pages call this for hundreds of tiles in one render)
  let cache = null, cacheAt = 0;
  function savedSplit(id){
    if (!cache || Date.now() - cacheAt > 3000){
      try { cache = JSON.parse(localStorage.getItem('verdicts:weapons') || 'null') || { m: {} }; } catch { cache = { m: {} }; }
      cacheAt = Date.now();
    }
    const x = cache.m[id]; return x && x[4] ? x[4] : null;
  }
  window.addEventListener('storage', e => { if (e.key === 'verdicts:weapons') cache = null; if (e.key === 'verdicts:armor') acache = null; });
  // keep / trash label for any weapon or armor instance, from the last Weapons / Armor triage scans
  let acache = null, acacheAt = 0;
  function savedLabel(id){
    savedSplit(id);   // refreshes the weapons cache
    const w = cache.m[id];
    if (w){
      const [v, , , old] = w, sp = w[4] || null;
      const L = { god: ['GOD', 'god', 'God roll'], close: ['CLOSE', 'close', 'Close'], trash: ['TRASH', 'trash', 'Trash'], exotic: ['EXO', 'exo', 'Exotic'] }[v] || (old ? ['OLD', 'old', 'Old gear'] : ['?', 'unr', 'Unrated']);
      return { tag: L[0], cls: L[1], label: L[2], short: modeShort(sp), split: sp };
    }
    if (!acache || Date.now() - acacheAt > 3000){ try { acache = JSON.parse(localStorage.getItem('verdicts:armor') || 'null') || { m: {} }; } catch { acache = { m: {} }; } acacheAt = Date.now(); }
    const a = acache.m[id];
    if (!a) return null;
    const [v, , legacy, exotic] = a;
    const L = v === 'trash' ? ['TRASH', 'trash', 'Trash'] : legacy && exotic ? ['OLD', 'oldx', 'Old exotic'] : legacy || v === 'legacy' ? ['OLD', 'old', 'Old gear'] : v === 'review' ? ['REVIEW', 'review', 'Review'] : ['KEEP', 'keep', 'Keep'];
    return { tag: L[0], cls: L[1], label: L[2], short: '', split: null };
  }
  Object.assign(window, { savedLabel, modeSplit, weaponModes, modeGraph, modeShort, modeDecide: decide, modeGrade: grade, savedSplit });
})();

/* Gear tier diamonds down the left edge of an item icon, like DIM. tierIcon wraps an <img> so the pips sit on it. */
(function(){
  function tierPips(t){
    t = Math.max(0, Math.min(5, +t || 0));
    return t ? '<span class="tpips t' + t + '" title="Tier ' + t + '">' + '<i></i>'.repeat(t) + '</span>' : '';
  }
  function tierIcon(imgHtml, t){ return +t ? '<span class="ticon">' + imgHtml + tierPips(t) + '</span>' : imgHtml; }
  Object.assign(window, { tierPips, tierIcon });
})();

/* Signed-in account lookup, cached for the browser session per sign-in token: every page used to ask Bungie
   GetMembershipsForCurrentUser on each load, a full round trip before the profile could even start. */
(function(){
  window.myMemberships = async function(bungieFn){
    let tok = '';
    try { tok = ((JSON.parse(localStorage.getItem('auth') || 'null') || {}).token || '').slice(-16); } catch {}
    try { const c = JSON.parse(sessionStorage.getItem('acctMe') || 'null'); if (c && tok && c.tok === tok && c.me) return c.me; } catch {}
    const me = await bungieFn('/User/GetMembershipsForCurrentUser/');
    try { if (tok) sessionStorage.setItem('acctMe', JSON.stringify({ tok, me: { destinyMemberships: me.destinyMemberships || [], primaryMembershipId: me.primaryMembershipId } })); } catch {}
    return me;
  };
})();
