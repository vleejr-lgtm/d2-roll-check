# Tower page: pins at the Tower only, glow reasons (turn-ins, blocked turn-ins, rank reward), loot pool panel on hover,
# can't-get reasons, roll popup from the single-vendor read, Move pins saved.
import json, asyncio, datetime
from playwright.async_api import async_playwright
ZAV, SHX, BAN, HID, NES = 69482069, 3603221665, 672118013, 5560, 7770
VENG, CENG, GLIM, ZW, ZW2, CW, BW, P1, P2, P3, P4 = 101, 102, 103, 201, 202, 203, 204, 501, 502, 503, 504
lite = {
  str(VENG): {"displayProperties": {"name": "Vanguard Engram", "icon": "/ve.png"}, "itemTypeDisplayName": "Engram", "itemType": 8},
  str(CENG): {"displayProperties": {"name": "Crucible Engram", "icon": "/ce.png"}, "itemTypeDisplayName": "Engram", "itemType": 8},
  str(GLIM): {"displayProperties": {"name": "Glimmer", "icon": "/g.png"}, "itemTypeDisplayName": "Currency", "itemType": 0},
  str(ZW): {"displayProperties": {"name": "Vanguard Pulse", "icon": "/z.png"}, "itemTypeDisplayName": "Pulse Rifle", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 2465295065}},
  str(ZW2): {"displayProperties": {"name": "Pricey Scout", "icon": "/z2.png"}, "itemTypeDisplayName": "Scout Rifle", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}},
  str(CW): {"displayProperties": {"name": "Crucible Hand Cannon", "icon": "/c.png"}, "itemTypeDisplayName": "Hand Cannon", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}},
  str(BW): {"displayProperties": {"name": "Banshee Auto", "icon": "/b.png"}, "itemTypeDisplayName": "Auto Rifle", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}},
  str(P1): {"displayProperties": {"name": "Outlaw"}, "itemTypeDisplayName": "Trait", "itemType": 19},
  str(P2): {"displayProperties": {"name": "Rampage"}, "itemTypeDisplayName": "Trait", "itemType": 19},
  str(P3): {"displayProperties": {"name": "Arrowhead Brake"}, "itemTypeDisplayName": "Barrel", "itemType": 19},
  str(P4): {"displayProperties": {"name": "Appended Mag"}, "itemTypeDisplayName": "Magazine", "itemType": 19},
}
future = (datetime.datetime.utcnow() + datetime.timedelta(days=4)).strftime('%Y-%m-%dT17:00:00Z')
V = lambda h, **k: dict({"vendorHash": h, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True}, **k)
vendors = {
  "vendors": {"data": {str(ZAV): V(ZAV), str(SHX): V(SHX), str(BAN): V(BAN, progression={"level": 16, "rewardItemStates": [6, 2]}), str(HID): V(HID), str(NES): V(NES)}},
  "categories": {"data": {str(ZAV): {"categories": [{"displayCategoryIndex": 0, "itemIndexes": [0]}, {"displayCategoryIndex": 1, "itemIndexes": [1]}]}}},
  "sales": {"data": {
    str(ZAV): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": ZW, "costs": [{"itemHash": VENG, "quantity": 1}], "saleStatus": 0, "augments": 8},
                             "1": {"vendorItemIndex": 1, "itemHash": ZW2, "costs": [{"itemHash": GLIM, "quantity": 999999}], "saleStatus": 2}}},
    str(SHX): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": CW, "costs": [{"itemHash": CENG, "quantity": 1}], "saleStatus": 1, "failureIndexes": [0]}}},
    str(BAN): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": BW, "costs": [{"itemHash": GLIM, "quantity": 500}], "saleStatus": 0}}},
    str(HID): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": BW, "costs": [], "saleStatus": 0}}},
    str(NES): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": BW, "costs": [], "saleStatus": 0}}}}}}
single = {"sales": {"data": vendors["sales"]["data"][str(BAN)]["saleItems"]},
  "itemComponents": {"sockets": {"data": {"0": {"sockets": [{"plugHash": h, "isVisible": True} for h in [P3, P4, P1, P2]]}}},
                     "reusablePlugs": {"data": {"0": {"plugs": {"2": [{"plugItemHash": P1, "canInsert": True}, {"plugItemHash": P2, "canInsert": True}]}}}},
                     "stats": {"data": {"0": {"stats": {"4284893193": {"statHash": 4284893193, "value": 600}, "4043523819": {"statHash": 4043523819, "value": 44}}}}}}}
ents = {
  "DestinyVendorDefinition/%d" % ZAV: {"displayProperties": {"name": "Commander Zavala", "icon": "/z.png"}, "visible": True, "locations": [{"destinationHash": 9001}],
      "displayCategories": [{"displayProperties": {"name": "Vanguard Engram ({var:123})"}}, {"displayProperties": {"name": "Weapons"}}], "failureStrings": []},
  "DestinyVendorDefinition/%d" % SHX: {"displayProperties": {"name": "Lord Shaxx", "icon": "/s.png"}, "visible": True, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": ["Make room in your inventory first."]},
  "DestinyVendorDefinition/%d" % BAN: {"displayProperties": {"name": "Banshee-44", "icon": "/b.png"}, "visible": True, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % HID: {"displayProperties": {"name": "Hidden Preview"}, "visible": False, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % NES: {"displayProperties": {"name": "Failsafe"}, "visible": True, "locations": [{"destinationHash": 9003}], "displayCategories": [], "failureStrings": []},
  "DestinyDestinationDefinition/9001": {"displayProperties": {"name": "The Last City"}, "placeHash": 8001},
  "DestinyDestinationDefinition/9003": {"displayProperties": {"name": "Nessus"}, "placeHash": 8003},
  "DestinyPlaceDefinition/8001": {"displayProperties": {"name": "Earth"}},
  "DestinyPlaceDefinition/8003": {"displayProperties": {"name": "Nessus"}},
  "DestinyStatDefinition/4284893193": {"displayProperties": {"name": "Rounds Per Minute"}},
  "DestinyStatDefinition/4043523819": {"displayProperties": {"name": "Impact"}},
}
prof = {"profileInventory": {"data": {"items": [{"itemHash": CENG, "quantity": 2, "bucketHash": 1469714392}]}},
        "profileCurrencies": {"data": {"items": [{"itemHash": VENG, "quantity": 2}, {"itemHash": GLIM, "quantity": 1000}]}},
        "characters": {"data": {"c1": {"characterId": "c1", "classType": 1, "light": 550, "dateLastPlayed": "2026-11-25T00:00:00Z"}}},
        "characterInventories": {"data": {"c1": {"items": []}}}, "characterEquipment": {"data": {"c1": {"items": []}}}, "itemComponents": {"instances": {"data": {}}}}
ok = lambda r: {"ErrorCode": 1, "Response": r}
calls = []
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--disable-web-security']); pg = await b.new_page(viewport={'width': 1500, 'height': 1000})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    async def route(rt):
      u = rt.request.url
      if u.startswith('file://'): return await rt.continue_()
      body = ok({})
      if 'Destiny2/Manifest' in u and u.rstrip('/').endswith('Manifest'): body = ok({"version": "tw1", "jsonWorldComponentContentPaths": {"en": {"DestinyInventoryItemLiteDefinition": "/c/lite.json"}}})
      elif u.endswith('/c/lite.json'): body = lite
      elif 'GetMembershipsForCurrentUser' in u: body = ok({"destinyMemberships": [{"membershipType": 3, "membershipId": "42"}], "primaryMembershipId": "42"})
      elif '/Vendors/%d/' % BAN in u: calls.append('single'); body = ok(single)
      elif '/Vendors/' in u: calls.append('vendors'); body = ok(vendors)
      elif '/Manifest/' in u:
        parts = u.rstrip('/').split('/'); body = ok(ents.get(parts[-2] + '/' + parts[-1], {}))
      elif '/Profile/' in u: body = ok(prof)
      await rt.fulfill(status=200, content_type='application/json', body=json.dumps(body))
    await pg.route('**/*', route)
    await pg.add_init_script("localStorage.setItem('apiKey','k'); localStorage.setItem('auth', JSON.stringify({token:'T', exp: Date.now()+3600e3}));")
    await pg.goto('file:///home/claude/godroll-checker/tower.html'); await pg.wait_for_selector('.twpin', timeout=20000); await pg.wait_for_timeout(300)
    pins = await pg.eval_on_selector_all('.twpin', "e => e.map(p => p.querySelector('.tlbl').textContent + (p.classList.contains('glow') ? ' GLOW' : '') + (p.classList.contains('new') ? ' NEW' : ''))")
    print('PINS:', pins)
    print('TIP shaxx:', await pg.get_attribute('.twpin[data-vh="%d"]' % SHX, 'title'))
    print('TIP zavala:', await pg.get_attribute('.twpin[data-vh="%d"]' % ZAV, 'title'))
    print('TIP banshee:', await pg.get_attribute('.twpin[data-vh="%d"]' % BAN, 'title'))
    print('STATUS:', await pg.inner_text('#status'))
    await pg.hover('.twpin[data-vh="%d"]' % ZAV); await pg.wait_for_timeout(500)
    print('PANEL zavala:', (await pg.inner_text('#twPanel')).replace('\n', ' | '))
    await pg.hover('.twpin[data-vh="%d"]' % BAN); await pg.wait_for_timeout(700)
    print('PANEL banshee:', (await pg.inner_text('#twPanel')).replace('\n', ' | '), '| single calls:', calls.count('single'))
    await pg.mouse.move(700, 900); await pg.wait_for_timeout(100)
    print('panel stays after hover moves off (hover-opened, sticky until close):', await pg.is_visible('#twPanel'))
    await pg.hover('#twPanel .nm.rl'); await pg.wait_for_timeout(900)
    print('ROLLPOP:', (await pg.inner_text('#rollPop')).replace('\n', ' | ')[:220], '| hidden:', await pg.eval_on_selector('#rollPop', 'e => e.classList.contains("hidden")'))
    await pg.screenshot(path='tower.png')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
    print('closed by Esc:', await pg.is_hidden('#twPanel'))
    await pg.click('#twArrange')
    box = await pg.eval_on_selector('.twpin[data-vh="%d"]' % ZAV, 'e => { const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }')
    await pg.mouse.move(box[0], box[1]); await pg.mouse.down(); await pg.mouse.move(box[0] - 200, box[1] - 120, steps=6); await pg.mouse.up()
    await pg.click('#twArrange'); await pg.wait_for_timeout(100)
    print('towerPos:', await pg.evaluate("localStorage.getItem('towerPos')"), '| panel after drag:', await pg.is_visible('#twPanel'))
    await pg.click('#twList .twrowv'); await pg.wait_for_timeout(200)
    print('list click opens:', await pg.is_visible('#twPanel'), (await pg.inner_text('#twPanel h3')))
    await pg.keyboard.press('Escape')
    print('nav:', await pg.eval_on_selector_all('header .tabs a', 'e=>e.map(x=>x.textContent+(x.classList.contains("active")?"*":""))'))
    await pg.screenshot(path='tower_full.png', full_page=True)
    print('errors', errs); await b.close()
asyncio.run(main())
