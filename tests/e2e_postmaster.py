import json, asyncio
from playwright.async_api import async_playwright
OPEN_DRAWERS = "new MutationObserver(() => document.querySelectorAll('details.drawer:not([open]), details.tagpop:not([open])').forEach(d => d.open = true)).observe(document, { subtree: true, childList: true });"
lite = {}; coll = {}
def sh(h, name, ch, src, idx, cat=True, **kw):
  lite[str(h)] = {"displayProperties": {"name": name, "icon": "/s%d.png" % h}, "itemType": 19, "itemSubType": 20 if not cat else 0, "itemCategoryHashes": [41] if cat else [], "collectibleHash": ch, "index": idx, "iconWatermark": "/wm.png", "inventory": {"tierTypeName": "Legendary"}, **kw}
  if ch: coll[str(ch)] = {"displayProperties": {"name": name}, "sourceString": src, "itemHash": h}
sh(1, "Gilded Sunrise", 1001, "Source: Eververse", 50)
sh(2, "Nightfall Ember", 1002, "Source: Vanguard Ops and Nightfall", 40)
sh(3, "Trials Glow", 1003, "Source: Trials of Osiris", 60)
sh(4, "Gambit Moss", 1004, "Source: Gambit", 10)
sh(5, "Raid Bone", 1005, "Source: Salvation's Edge raid", 70)
sh(6, "Solstice Flare", 1006, "Source: Solstice event", 20, cat=False)
sh(7, "EDZ Rust", 1007, "Source: Patrol in the EDZ", 30)
sh(8, "Default Shader", 0, "", 5)                       # no collectible -> excluded
sh(9, "Gilded Sunrise", 1009, "Source: Eververse", 90)  # same name newer collectible -> wins
sh(10, "Mystery", 1010, "Source: something odd", 15)
lite["500"] = {"displayProperties": {"name": "Some Gun", "icon": "/g.png"}, "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}}
lite["501"] = {"displayProperties": {"name": "Locked Exotic", "icon": "/g.png"}, "itemType": 3, "inventory": {"tierType": 2, "bucketTypeHash": 1498876634}}
lite["502"] = {"displayProperties": {"name": "Good Legendary", "icon": "/g.png"}, "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}}
lite["503"] = {"displayProperties": {"name": "Junk Rare", "icon": "/g.png"}, "itemType": 3, "inventory": {"tierType": 4, "bucketTypeHash": 1498876634}}
lite["600"] = {"displayProperties": {"name": "Enhancement Core", "icon": "/c.png"}, "itemType": 0, "inventory": {"bucketTypeHash": 1469714392}}
prof = {"profileInventory": {"data": {"items": []}}, "characters": {"data": {"c1": {"characterId": "c1", "classType": 1, "light": 2000, "dateLastPlayed": "2026-11-25T00:00:00Z"}}},
  "characterInventories": {"data": {"c1": {"items": [{"itemHash": 501, "itemInstanceId": "K1", "bucketHash": 1498876634, "state": 1}, {"itemHash": 502, "itemInstanceId": "K2", "bucketHash": 1498876634}, {"itemHash": 503, "itemInstanceId": "K3", "bucketHash": 1498876634}, {"itemHash": 500, "itemInstanceId": "PM1", "bucketHash": 215593132, "quantity": 1}, {"itemHash": 600, "bucketHash": 215593132, "quantity": 3}, {"itemHash": 700, "bucketHash": 215593132, "quantity": 1}]}}}, "characterEquipment": {"data": {"c1": {"items": [{"itemHash": 502, "itemInstanceId": "EQ1", "bucketHash": 1498876634}]}}}, "itemComponents": {"instances": {"data": {}}},
  "profileCollectibles": {"data": {"collectibles": {"1009": {"state": 0}, "1002": {"state": 1}, "1003": {"state": 0}, "1004": {"state": 1}, "1005": {"state": 1}, "1006": {"state": 1}, "1007": {"state": 1}, "1010": {"state": 1}}}},
  "characterCollectibles": {"data": {"c1": {"collectibles": {"1004": {"state": 0}}}}}}
ok = lambda r: {"ErrorCode": 1, "Response": r}
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--disable-web-security']); pg = await b.new_page(viewport={'width': 1440, 'height': 1000}); await pg.add_init_script(OPEN_DRAWERS)
    calls = []
    async def route(rt):
      u = rt.request.url
      if '/Manifest/DestinyInventoryItemDefinition/9101' in u: body = ok({"displayProperties": {"name": "Rampage", "icon": "/r.png"}, "itemTypeDisplayName": "Trait", "plug": {"plugCategoryIdentifier": "frames"}})
      elif '/Manifest/DestinyInventoryItemDefinition/700' in u: body = ok({"displayProperties": {"name": "Quest Thing", "icon": "/q.png"}, "inventory": {"bucketTypeHash": 1345459588}})
      elif '/Manifest/DestinyInventoryItemDefinition/' in u: body = ok({"seasonHash": 77})
      elif '/Manifest/DestinyInventoryBucketDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body = ok({'1498876634': {'itemCount': 4, 'category': 3}, '1469714392': {'itemCount': 50, 'category': 1}}.get(h, {}))
      elif '/Manifest/DestinySeasonDefinition/' in u: body = ok({"displayProperties": {"name": "Season of the Lawless"}, "seasonNumber": 28})
      elif 'Destiny2/Manifest' in u: body = ok({"version": "v9", "jsonWorldComponentContentPaths": {"en": {"DestinyInventoryItemLiteDefinition": "/c/lite.json", "DestinyCollectibleDefinition": "/c/coll.json"}}})
      elif '/c/lite.json' in u: calls.append('lite'); body = lite
      elif '/c/coll.json' in u: body = coll
      elif 'GetMembershipsForCurrentUser' in u: body = ok({"destinyMemberships": [{"membershipType": 3, "membershipId": "42"}], "primaryMembershipId": "42"})
      elif '/Item/' in u and '/Profile/' in u:
        body = ok({"instance":{"data":{"primaryStat":{"value":540}}},"stats":{"data":{"stats":{}}},"sockets":{"data":{"sockets":[{"plugHash":9101,"isVisible":True}]}}})
      elif 'PullFromPostmaster' in u:
        pb = json.loads(rt.request.post_data); calls.append(('pull', pb['itemReferenceHash'], pb['stackSize'], pb['itemId']))
        noroom = {"ErrorCode": 1642, "ErrorStatus": "DestinyNoRoomInDestination", "Message": "There are no item slots available to transfer this item."}
        if pb['itemReferenceHash'] == 500 and not any(c[0]=='vault' for c in calls if isinstance(c, tuple)): body = noroom
        elif pb['itemReferenceHash'] == 700: body = noroom
        else: body = ok(0)
      elif 'TransferItem' in u:
        pb = json.loads(rt.request.post_data); calls.append(('vault', pb['itemReferenceHash'], pb['itemId'], pb['transferToVault'])); body = ok(0)
      elif '/Profile/' in u: calls.append(u.split('components=')[1]); body = ok(prof)
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin": "*", "content-type": "application/json"})
    await pg.route('**/*', route)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    url = 'file:///home/claude/godroll-checker/shaders.html'
    await pg.goto(url); await pg.evaluate("() => { localStorage.clear(); localStorage.setItem('apiKey','k'); }")
    await pg.goto(url); await pg.wait_for_selector('.shcard', timeout=15000); await pg.wait_for_timeout(300)
    print('OUT status:', await pg.inner_text('#status'))
    print('OUT signin banner:', await pg.is_visible('#shSignin'))
    print('OUT sum:', (await pg.inner_text('#shSum')).replace('\n', ' | '))
    print('OUT cards:', await pg.eval_on_selector_all('.shcard .shname', 'e=>e.map(x=>x.textContent)'))
    print('OUT badge:', await pg.inner_text('.shcard .shst'))
    await pg.fill('#shSearch', 'eververse'); await pg.wait_for_timeout(250)
    print('search eververse:', await pg.eval_on_selector_all('.shcard .shname', 'e=>e.map(x=>x.textContent)'))
    await pg.fill('#shSearch', ''); await pg.wait_for_timeout(250)
    # signed in
    await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3}))")
    await pg.evaluate("localStorage.setItem('vendSales', JSON.stringify({at: Date.now(), vendors: [{n:'Ada-1', due: new Date(Date.now()+864e5).toISOString(), h:[3, 500]}, {n:'Eververse', due:null, h:[1]}]}))")
    await pg.goto(url); await pg.wait_for_selector('.shst.own', timeout=15000); await pg.wait_for_timeout(300)
    print('IN status:', await pg.inner_text('#status'), '| lite downloads:', calls.count('lite'), '| comps:', [c for c in calls if c != 'lite'])
    print('IN sum:', (await pg.inner_text('#shSum')).replace('\n', ' | '))
    print('IN pills:', (await pg.inner_text('#shStatus')).replace('\n', ' '))
    rows = lambda: pg.eval_on_selector_all('.shcard', "e=>e.map(x=>x.querySelector('.shname').textContent+':'+x.querySelector('.shst').textContent)")
    print('IN newest:', await rows())
    await pg.click('[data-st="need"]'); await pg.wait_for_timeout(150); print('need:', await rows())
    await pg.click('[data-st="own"]'); await pg.wait_for_timeout(150); print('own:', await rows())
    await pg.click('[data-st="all"]')
    for v in ['ever', 'van', 'pvp', 'gambit', 'raid', 'event', 'world', 'other']:
      await pg.select_option('#shSource', v); await pg.wait_for_timeout(100); print('src', v, await pg.eval_on_selector_all('.shcard .shname', 'e=>e.map(x=>x.textContent)'))
    await pg.select_option('#shSource', 'all')
    for v in ['name', 'owned', 'missing']:
      await pg.select_option('#shSort', v); await pg.wait_for_timeout(100); print('sort', v, await rows())
    await pg.select_option('#shSort', 'new')
    print('saved:', await pg.evaluate("[localStorage.getItem('shStatus'), localStorage.getItem('shSource'), localStorage.getItem('shSort')]"))
    await pg.click('.shcard[data-sh="3"]'); await pg.wait_for_timeout(600)
    print('MODAL:', (await pg.inner_text('#shModal')).replace('\n', ' | '))
    await pg.screenshot(path='/home/claude/tests/shaders_modal.png')
    await pg.keyboard.press('Escape'); print('closed:', await pg.is_hidden('#shModal'))
    await pg.click('.shcard[data-sh="2"]'); await pg.wait_for_timeout(400); print('MODAL2 vend:', await pg.inner_text('.shvend')); await pg.click('#shClose')
    await pg.screenshot(path='/home/claude/tests/shaders.png')
    print('PM button html:', await pg.inner_html('#btnPM'))
    print('PM button:', await pg.inner_text('#btnPM'), await pg.get_attribute('#btnPM','title'))
    await pg.click('#btnPM'); await pg.wait_for_timeout(600)
    print('PM panel:', (await pg.inner_text('#pmList')).replace('\n',' | '))
    await pg.screenshot(path='/home/claude/tests/postmaster.png')
    await pg.click('.pmrow[data-roll="PM1"] .pmname'); await pg.wait_for_timeout(800)
    print('PM ROLL:', (await pg.inner_text('#rollPop')).replace('\n',' | '))
    await pg.keyboard.press('Escape')
    print('PM buttons:', await pg.eval_on_selector_all('#pmList button', 'e=>e.map(x=>x.innerText)'))
    await pg.click('.pmrow[data-roll="PM1"] [data-pmv]'); await pg.wait_for_timeout(1500)
    print('vault calls:', [c for c in calls if isinstance(c, tuple)])
    print('after vault:', (await pg.inner_text('#pmList')).replace('\n',' | '))
    await pg.click('[data-pmall="c1"]'); await pg.wait_for_timeout(1500)
    print('pull calls:', [c for c in calls if isinstance(c, tuple)])
    print('after:', (await pg.inner_text('#pmList')).replace('\n',' | '), '| btn:', await pg.inner_text('#btnPM'))
    print('status:', repr(await pg.inner_text('#status')))
    print('nav:', await pg.eval_on_selector_all('header .tabs a', 'e=>e.map(x=>x.textContent+(x.classList.contains("active")?"*":""))'))
    print('errors', errs); await b.close()
asyncio.run(main())
