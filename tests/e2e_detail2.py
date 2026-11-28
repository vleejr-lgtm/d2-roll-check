import json, asyncio
from playwright.async_api import async_playwright
# A weapon whose "weapon perks" category also holds an empty enhancement socket and the masterwork socket
W = 9000
S_RANGE, S_STAB, S_HAND, S_MAG, S_RELOAD = 11, 12, 13, 14, 15
CAT_PERKS, CAT_INTR, CAT_MODS = 4241085061, 3956125808, 2685412949
ST_MW, ST_MOD, ST_PERK = 801, 802, 803
PS = {'barrel': 701, 'mag': 702, 't1': 703, 't2': 704, 'mw': 705, 'mods': 706}
def plug(h, name, typ, cat, icon='/p.png', stats=None):
    return str(h), {"hash": h, "displayProperties": {"name": name, "icon": icon, "description": name + " description"}, "itemTypeDisplayName": typ,
                    "plug": {"plugCategoryIdentifier": cat}, "investmentStats": [{"statTypeHash": s, "value": v, "isConditionallyActive": False} for s, v in (stats or [])]}
P = dict([
  plug(100, 'Adaptive Frame', 'Intrinsic', 'intrinsics'),
  plug(101, 'Arrowhead Brake', 'Barrel', 'barrels', stats=[(S_HAND, 10)]),
  plug(102, 'Corkscrew Rifling', 'Barrel', 'barrels', stats=[(S_RANGE, 5), (S_STAB, 5), (S_HAND, 5)]),
  plug(111, 'Accurized Rounds', 'Magazine', 'magazines', stats=[(S_RANGE, 10)]),
  plug(112, 'Appended Mag', 'Magazine', 'magazines', stats=[(S_MAG, 4)]),
  plug(121, 'Outlaw', 'Trait', 'frames'),
  plug(122, 'Outlaw', 'Enhanced Trait', 'frames', stats=[(S_RELOAD, 5)]),
  plug(123, 'Rapid Hit', 'Trait', 'frames'),
  plug(131, 'Rampage', 'Trait', 'frames'),
  plug(132, 'Kill Clip', 'Trait', 'frames'),
  plug(141, 'Veist Stinger', 'Origin Trait', 'origins'),
  plug(150, 'Empty Enhancement Socket', 'Enhancement', 'crafting.plugs.weapons.mods.enhancers', icon=''),
  plug(160, 'Masterwork', 'Masterwork', 'v400.plugs.weapons.masterworks.stat.empty'),
  plug(161, 'Masterworked: Range', 'Masterwork', 'v400.plugs.weapons.masterworks.stat.range', stats=[(S_RANGE, 10)]),
  plug(162, 'Range Tier 5', 'Masterwork', 'v400.plugs.weapons.masterworks.stat.range', stats=[(S_RANGE, 5)]),
  plug(163, 'Masterworked: Stability', 'Masterwork', 'v400.plugs.weapons.masterworks.stat.stability', stats=[(S_STAB, 10)]),
  plug(164, 'Masterworked: Handling', 'Masterwork', 'v400.plugs.weapons.masterworks.stat.handling', stats=[(S_HAND, 10)]),
  plug(170, 'Empty Mod Socket', 'Weapon Mod', 'v400.weapon.mod_empty'),
  plug(171, 'Backup Mag', 'Weapon Mod', 'v400.weapon.mod_magazine', stats=[(S_MAG, 3)]),
  plug(172, 'Counterbalance Stock', 'Weapon Mod', 'v400.weapon.mod_guns', stats=[(S_STAB, 0)]),
  plug(173, 'Targeting Adjuster', 'Weapon Mod', 'v400.weapon.mod_guns'),
  plug(174, 'Quick Access Sling', 'Weapon Mod', 'v400.weapon.mod_guns', stats=[(S_HAND, 0)]),
])
weapon = {"hash": W, "displayProperties": {"name": "Test Cannon", "icon": "/w.png"}, "itemTypeDisplayName": "Hand Cannon", "screenshot": "/s.jpg",
  "defaultDamageTypeHash": 3373582085, "equippingBlock": {"ammoType": 1},
  "investmentStats": [{"statTypeHash": s, "value": v} for s, v in [(S_RANGE, 40), (S_STAB, 40), (S_HAND, 40), (S_MAG, 12), (S_RELOAD, 40)]],
  "stats": {"statGroupHash": 600, "stats": {}},
  "sockets": {"socketEntries": [
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 100},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 101, "randomizedPlugSetHash": PS['barrel']},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 111, "randomizedPlugSetHash": PS['mag']},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 121, "randomizedPlugSetHash": PS['t1']},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 131, "randomizedPlugSetHash": PS['t2']},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 141},
     {"socketTypeHash": ST_PERK, "singleInitialItemHash": 150},
     {"socketTypeHash": ST_MW, "singleInitialItemHash": 160, "reusablePlugSetHash": PS['mw']},
     {"socketTypeHash": ST_MOD, "singleInitialItemHash": 170, "reusablePlugSetHash": PS['mods']}],
   "socketCategories": [{"socketCategoryHash": CAT_INTR, "socketIndexes": [0]}, {"socketCategoryHash": CAT_PERKS, "socketIndexes": [1, 2, 3, 4, 5, 6, 7]}, {"socketCategoryHash": CAT_MODS, "socketIndexes": [8]}]}}
pset = lambda hs: {"reusablePlugItems": [{"plugItemHash": h, "currentlyCanRoll": True} for h in hs]}
ents = {('DestinyInventoryItemDefinition', W): weapon,
  ('DestinyPlugSetDefinition', PS['barrel']): pset([101, 102]), ('DestinyPlugSetDefinition', PS['mag']): pset([111, 112]),
  ('DestinyPlugSetDefinition', PS['t1']): pset([121, 122, 123]), ('DestinyPlugSetDefinition', PS['t2']): pset([131, 132]),
  ('DestinyPlugSetDefinition', PS['mw']): pset([160, 161, 162, 163, 164]), ('DestinyPlugSetDefinition', PS['mods']): pset([170, 171, 172, 173, 174]),
  ('DestinySocketTypeDefinition', ST_MW): {"plugWhitelist": [{"categoryIdentifier": "v400.plugs.weapons.masterworks.stat.range"}]},
  ('DestinySocketTypeDefinition', ST_MOD): {"plugWhitelist": [{"categoryIdentifier": "v400.weapon.mod_guns"}, {"categoryIdentifier": "v400.weapon.mod_magazine"}]},
  ('DestinySocketTypeDefinition', ST_PERK): {"plugWhitelist": [{"categoryIdentifier": "frames"}]},
  ('DestinyDamageTypeDefinition', 3373582085): {"displayProperties": {"name": "Kinetic"}},
  ('DestinyStatGroupDefinition', 600): {"scaledStats": [{"statHash": s, "maximumValue": 100, "displayInterpolation": [{"value": 0, "weight": 0}, {"value": 100, "weight": 100}]} for s in [S_RANGE, S_STAB, S_HAND, S_RELOAD]] + [{"statHash": S_MAG, "displayAsNumeric": True, "maximumValue": 100, "displayInterpolation": [{"value": 0, "weight": 0}, {"value": 100, "weight": 100}]}]},
}
for h, n in [(S_RANGE, 'Range'), (S_STAB, 'Stability'), (S_HAND, 'Handling'), (S_MAG, 'Magazine'), (S_RELOAD, 'Reload Speed')]: ents[('DestinyStatDefinition', h)] = {"displayProperties": {"name": n}}
for k, v in P.items(): ents[('DestinyInventoryItemDefinition', int(k))] = v
lite = {k: {"displayProperties": {"name": v["displayProperties"]["name"], "icon": v["displayProperties"]["icon"]}, "itemTypeDisplayName": v["itemTypeDisplayName"], "itemType": 19} for k, v in P.items()}
lite[str(W)] = {"displayProperties": {"name": "Test Cannon", "icon": "/w.png"}, "itemTypeDisplayName": "Hand Cannon", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}}
ok = lambda r: {"ErrorCode": 1, "Response": r}
calls = []
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--disable-web-security']); pg = await b.new_page(viewport={'width': 1400, 'height': 1000})
    async def route(rt):
      u = rt.request.url
      parts = u.rstrip('/').split('/')
      if '/Destiny2/Manifest/' in u and parts[-1].isdigit():
        body = ok(ents.get((parts[-2], int(parts[-1])), {}))
      elif 'Destiny2/Manifest' in u: body = ok({"version": "v1", "jsonWorldComponentContentPaths": {"en": {"DestinyInventoryItemLiteDefinition": "/c/lite.json"}}})
      elif '/c/lite.json' in u: body = lite
      elif '/Actions/' in u: calls.append(u.split('/Actions/')[1]); body = ok(0)
      elif u.endswith(('.png', '.jpg')): return await rt.fulfill(body=b'')
      elif 'raw.githubusercontent' in u: return await rt.fulfill(body='', headers={"access-control-allow-origin": "*"})
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin": "*", "content-type": "application/json"})
    await pg.route('**/*', route)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    url = 'file:///home/claude/godroll-checker/index.html'
    await pg.goto(url); await pg.evaluate("() => { localStorage.clear(); localStorage.setItem('apiKey','k'); }"); await pg.goto(url)
    await pg.evaluate("async () => { await loadDefs(); }")
    stats = lambda: pg.eval_on_selector_all('#dbody .srow', "els => els.map(e => e.innerText.replace(/\\s+/g,' ').trim())")
    # ---- lookup (not owned) ----
    await pg.evaluate(f"() => openDetail(null, {W})"); await pg.wait_for_selector('.pcols .pcol', timeout=10000); await pg.wait_for_timeout(200)
    print('HEADER:', (await pg.inner_text('.dhead .meta')), '|', await pg.inner_text('.dstatus .where'))
    print('COLUMNS:', await pg.eval_on_selector_all('.pcol .phead', 'els => els.map(e => e.textContent)'))
    print('perk icons per column:', await pg.eval_on_selector_all('.pcol', 'els => els.map(e => e.querySelectorAll(".perk-o").length)'))
    print('Enhanced toggle:', await pg.is_visible('#dEnh'))
    print('MODS:', await pg.eval_on_selector_all('.mod-o', 'els => els.map(e => e.title)'))
    print('MW:', await pg.eval_on_selector_all('.mw-o', 'els => els.map(e => e.innerText.replace(/\\s+/g," "))'))
    print('stats base:', await stats())
    await pg.click('.mw-o:has-text("Range")'); await pg.wait_for_timeout(100)
    print('after MW Range:', await stats(), '| selected:', await pg.inner_text('.mw-o.sel'))
    await pg.click('.mod-o[title="Backup Mag"]'); await pg.wait_for_timeout(100)
    print('after Backup Mag:', [s for s in await stats() if 'Magazine' in s], '| mod selected:', await pg.eval_on_selector_all('.mod-o.sel', 'els => els.map(e => e.title)'))
    await pg.click('.mod-o[title="Backup Mag"]'); await pg.wait_for_timeout(100)
    print('Backup Mag clicked again (off):', [s for s in await stats() if 'Magazine' in s])
    await pg.click('#dEnh'); await pg.wait_for_timeout(100)
    print('Enhanced on -> Perk 1 shows enhanced:', await pg.eval_on_selector_all('.pcol:nth-child(3) .perk-o.enh', 'els => els.length'))
    await pg.click('#dEnh'); await pg.wait_for_timeout(100)
    # save my god roll still works (perks only)
    await pg.click('.pcol:nth-child(3) .perk-o[data-plug="123"]'); await pg.click('.pcol:nth-child(4) .perk-o[data-plug="132"]'); await pg.wait_for_timeout(100)
    await pg.click('#dSave'); await pg.wait_for_timeout(200)
    print('MY ROLL saved:', await pg.evaluate("JSON.stringify(myRolls())"))
    await pg.screenshot(path='/home/claude/tests/detail_lookup.png')
    await pg.keyboard.press('Escape')
    # ---- one of your copies: Range masterwork + Backup Mag on it ----
    await pg.evaluate("""() => { state.acct = { membershipType: 3, membershipId: '42' }; localStorage.setItem('auth', JSON.stringify({ token: 'T', exp: Date.now() + 3600e3 }));
      window._it = { id: 'c1', hash: %d, name: 'Test Cannon', loc: 'Hunter', charId: 'h1', power: 550, gearTier: 5, locked: false, equipped: false,
        r: { verdict: 'god', reason: 'Matches a recommended roll' }, score: 84, aegis: 'A',
        cur: { 0: 100, 1: 101, 2: 111, 3: 121, 4: 131, 5: 141, 6: 150, 7: 161, 8: 171 },
        owned: { 1: [101, 102], 2: [111, 112], 3: [121, 123], 4: [131, 132] }, sel: new Set() };
      state.chars = [{ id: 'h1', name: 'Hunter' }]; state.activeChar = 'h1';
      return openDetail(window._it, %d); }""" % (W, W))
    await pg.wait_for_selector('.pcols .pcol', timeout=10000); await pg.wait_for_timeout(200)
    print('COPY status:', await pg.inner_text('.dstatus .where'))
    print('COPY MW selected:', await pg.inner_text('.mw-o.sel'), '| mod selected:', await pg.eval_on_selector_all('.mod-o.sel', 'els => els.map(e => e.title)'))
    print('COPY stats:', await stats())
    await pg.click('.mw-o:has-text("Stability")'); await pg.wait_for_timeout(100)
    print('MW -> Stability:', [s for s in await stats() if 'Range' in s or 'Stability' in s], '| Apply disabled (only MW changed):', await pg.is_disabled('#dApply'))
    await pg.click('.mw-o:has-text("No Masterwork")'); await pg.wait_for_timeout(100)
    print('No Masterwork:', [s for s in await stats() if 'Range' in s])
    await pg.click('.pcol:nth-child(1) .perk-o[data-plug="102"]'); await pg.wait_for_timeout(100)
    print('Barrel changed -> Apply enabled:', not await pg.is_disabled('#dApply'))
    await pg.screenshot(path='/home/claude/tests/detail_copy.png')
    calls.clear(); await pg.click('#dApply'); await pg.wait_for_timeout(1500)
    print('APPLY calls:', calls)
    print('errors', errs); await b.close()
asyncio.run(main())
