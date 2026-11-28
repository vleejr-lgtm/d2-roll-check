import json, asyncio, datetime
from playwright.async_api import async_playwright
W, XW, A, AR, CIPH, GLIM, ENG = 1001, 1002, 2001, 2002, 3001, 3002, 6001
GUN, P1, P2, P3, P4 = 4001, 5001, 5002, 5003, 5004
SW, SG, SS = 11, 12, 13   # stat hashes: Weapons, Grenade, Super
HELM = 3448274439
lite = {
  str(W): {"displayProperties": {"name": "Fixed Hand Cannon", "icon": "/w.png"}, "itemTypeDisplayName": "Hand Cannon", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 1498876634}},
  str(XW): {"displayProperties": {"name": "Xur Exotic Gun", "icon": "/x.png"}, "itemTypeDisplayName": "Auto Rifle", "itemType": 3, "inventory": {"tierType": 6, "bucketTypeHash": 2465295065}},
  str(A): {"displayProperties": {"name": "Gunner Helm", "icon": "/a.png"}, "itemTypeDisplayName": "Helmet", "itemType": 2, "classType": 1, "inventory": {"tierType": 5, "bucketTypeHash": HELM}},
  str(AR): {"displayProperties": {"name": "Random Gloves", "icon": "/a.png"}, "itemTypeDisplayName": "Gauntlets", "itemType": 2, "classType": 1, "inventory": {"tierType": 5, "bucketTypeHash": 3551918588}},
  str(CIPH): {"displayProperties": {"name": "Exotic Cipher"}, "itemType": 0},
  str(GLIM): {"displayProperties": {"name": "Glimmer"}, "itemType": 0},
  str(ENG): {"displayProperties": {"name": "Exotic Engram", "icon": "/e.png"}, "itemTypeDisplayName": "Engram", "itemType": 8},
  str(GUN): {"displayProperties": {"name": "Gunner"}, "itemTypeDisplayName": "Archetype", "itemType": 19},
  str(P1): {"displayProperties": {"name": "Outlaw"}, "itemTypeDisplayName": "Trait", "itemType": 19},
  str(P2): {"displayProperties": {"name": "Rampage"}, "itemTypeDisplayName": "Trait", "itemType": 19},
  str(P3): {"displayProperties": {"name": "Arrowhead Brake"}, "itemTypeDisplayName": "Barrel", "itemType": 19},
  str(P4): {"displayProperties": {"name": "Appended Mag"}, "itemTypeDisplayName": "Magazine", "itemType": 19},
}
wl = "title:test\n//notes:great pve roll|tags:pve,god\ndimwishlist:item=%d&perks=%d,%d,%d,%d\ndimwishlist:item=%d&perks=%d,%d,%d,%d\n" % (W, P3, P4, P1, P2, 1003, P3, P4, P1, P2)
S = lambda hs: {"sockets": [{"plugHash": h, "isVisible": True} for h in hs]}
future = (datetime.datetime.utcnow() + datetime.timedelta(days=4)).strftime('%Y-%m-%dT17:00:00Z')
XUR = 2190858386
ZAV, SHX, FOCUS, ZW = 69482069, 3603221665, 7001, 1003
WK, HID = 5550, 5560
lite[str(FOCUS)] = {"displayProperties": {"name": "Random Gloves", "icon": "/f.png"}, "itemTypeDisplayName": "Focused Decoding", "itemType": 20}
lite[str(ZW)] = {"displayProperties": {"name": "Zavala Pulse", "icon": "/z.png"}, "itemTypeDisplayName": "Pulse Rifle", "itemType": 3, "inventory": {"tierType": 5, "bucketTypeHash": 2465295065}}
vendors = {
  "vendors": {"data": {"111": {"vendorHash": 111, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True},
                       str(WK): {"vendorHash": WK, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True},
                       str(HID): {"vendorHash": HID, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True},
                       str(XUR): {"vendorHash": XUR, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True},
                       str(ZAV): {"vendorHash": ZAV, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True},
                       str(SHX): {"vendorHash": SHX, "vendorLocationIndex": 0, "nextRefreshDate": future, "enabled": True}}},
  "categories": {"data": {"111": {"categories": [{"displayCategoryIndex": 0, "itemIndexes": [0, 1, 2]}]}}},
  "sales": {"data": {
    "111": {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": W, "costs": [{"itemHash": GLIM, "quantity": 50000}], "saleStatus": 0},
                          "1": {"vendorItemIndex": 1, "itemHash": A, "costs": [{"itemHash": GLIM, "quantity": 20000}], "saleStatus": 0},
                          "2": {"vendorItemIndex": 2, "itemHash": AR, "costs": [], "saleStatus": 0}}},
    str(ZAV): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": ZW, "costs": [], "saleStatus": 0}}},
    str(WK): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": W, "costs": [], "saleStatus": 1}}},
    str(HID): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": W, "costs": [], "saleStatus": 0}}},
    str(SHX): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": AR, "costs": [], "saleStatus": 0}, "1": {"vendorItemIndex": 1, "itemHash": FOCUS, "costs": [], "saleStatus": 0}}},
    str(XUR): {"saleItems": {"0": {"vendorItemIndex": 0, "itemHash": XW, "costs": [{"itemHash": CIPH, "quantity": 1}], "saleStatus": 0},
                             "1": {"vendorItemIndex": 1, "itemHash": ENG, "costs": [{"itemHash": GLIM, "quantity": 97}], "saleStatus": 0}}}}},
  "itemComponents": {
    "111": {"sockets": {"data": {"0": S([P3, P4, P1, P2]), "1": S([GUN])}},
            "stats": {"data": {"1": {"stats": {str(SW): {"value": 30}, str(SG): {"value": 25}, str(SS): {"value": 20}}}}},
            "instances": {"data": {"1": {"gearTier": 5}}}},
    str(XUR): {"sockets": {"data": {"0": S([P1])}}},
    str(ZAV): {"sockets": {"data": {"0": S([P3, P4, P1, P2])}}, "reusablePlugs": {"data": {"0": {"plugs": {"2": [{"plugItemHash": P1, "canInsert": True}, {"plugItemHash": P2, "canInsert": True}]}}}}},
    str(HID): {"sockets": {"data": {"0": S([P3, P4, P1, P2])}}}}}
ents = {
  "DestinyVendorDefinition/111": {"displayProperties": {"name": "Banshee-44", "icon": "/b.png"}, "visible": True, "locations": [{"destinationHash": 9001}], "displayCategories": [{"displayProperties": {"name": "Weekly Wares"}}], "failureStrings": []},
  "DestinyVendorDefinition/%d" % XUR: {"displayProperties": {"name": "Xûr", "icon": "/xu.png"}, "visible": True, "locations": [{"destinationHash": 9002}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % WK: {"displayProperties": {"name": "Vanguard Arms Rewards", "icon": "/va.png"}, "visible": False, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % HID: {"displayProperties": {"name": "Collections Preview", "icon": "/cp.png"}, "visible": False, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % ZAV: {"displayProperties": {"name": "Commander Zavala", "icon": "/z.png"}, "visible": True, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyVendorDefinition/%d" % SHX: {"displayProperties": {"name": "Lord Shaxx", "icon": "/s.png"}, "visible": True, "locations": [{"destinationHash": 9001}], "displayCategories": [], "failureStrings": []},
  "DestinyDestinationDefinition/9001": {"displayProperties": {"name": "The Last City"}, "placeHash": 8001},
  "DestinyDestinationDefinition/9002": {"displayProperties": {"name": "Tower"}, "placeHash": 8001},
  "DestinyPlaceDefinition/8001": {"displayProperties": {"name": "Earth"}},
  "DestinyStatDefinition/11": {"displayProperties": {"name": "Weapons"}},
  "DestinyStatDefinition/12": {"displayProperties": {"name": "Grenade"}},
  "DestinyStatDefinition/13": {"displayProperties": {"name": "Super"}},
  "DestinyInventoryItemDefinition/%d" % A: {"classType": 1},
}
INV = [{"itemHash": W, "itemInstanceId": "w1", "state": 0}]
CH = []
prof = {"profileInventory": {"data": {"items": INV}},
        "characters": {"data": {"c1": {"characterId": "c1", "classType": 1, "light": 550, "dateLastPlayed": "2026-11-25T00:00:00Z"},
                                "c2": {"characterId": "c2", "classType": 0, "light": 540, "dateLastPlayed": "2026-11-20T00:00:00Z"}}},
        "characterInventories": {"data": {"c1": {"items": CH}}}, "characterEquipment": {"data": {"c1": {"items": []}}},
        "itemComponents": {"instances": {"data": {"w1": {"primaryStat": {"value": 550}}, "a9": {"primaryStat": {"value": 551}, "gearTier": 5}}}}}
ok = lambda r: {"ErrorCode": 1, "Response": r}
calls = []
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--disable-web-security']); pg = await b.new_page(viewport={'width': 1400, 'height': 1100})
    async def route(rt):
      u = rt.request.url
      if '/Destiny2/Manifest/' in u and u.rstrip('/').split('/')[-1].isdigit():
        k = '/'.join(u.rstrip('/').split('/')[-2:]); body = ok(ents.get(k, {}))
      elif 'Destiny2/Manifest' in u: body = ok({"version": "v9", "jsonWorldComponentContentPaths": {"en": {"DestinyInventoryItemLiteDefinition": "/common/lite.json"}}})
      elif 'lite.json' in u: body = lite
      elif 'GetMembershipsForCurrentUser' in u: body = ok({"destinyMemberships": [{"membershipType": 3, "membershipId": "42"}], "primaryMembershipId": "42"})
      elif '/Vendors/%d/' % WK in u:
        calls.append(('one', WK)); body = ok({"sales": {"data": vendors["sales"]["data"][str(WK)]["saleItems"]}, "itemComponents": {"sockets": {"data": {"0": S([P3, P4, P1, P2])}}}})
      elif '/Vendors/' in u: calls.append(('vendors', u.split('/Character/')[1])); body = ok(vendors)
      elif '/Profile/' in u: body = ok(prof)
      elif '/Actions/' in u: calls.append((u.split('/Actions/')[1], json.loads(rt.request.post_data))); body = ok(0)
      elif 'voltron' in u: return await rt.fulfill(body=wl, headers={"access-control-allow-origin": "*"})
      elif 'raw.githubusercontent' in u: return await rt.fulfill(body="", headers={"access-control-allow-origin": "*"})
      elif u.endswith(('.png', '.jpg')): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin": "*", "content-type": "application/json"})
    await pg.route('**/*', route)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    url = 'file:///home/claude/godroll-checker/vendors.html'
    await pg.goto(url)
    await pg.evaluate("""() => { localStorage.clear(); localStorage.setItem('apiKey','k'); localStorage.setItem('clientId','1');
      localStorage.setItem('auth', JSON.stringify({token:'T', exp: Date.now() + 3600e3}));
      localStorage.setItem('wlPresets', JSON.stringify({aegis:false,gigpve:false,gigpvp:false}));
      localStorage.setItem('armorIndex', JSON.stringify({at:1, m:{'1|Helmet|Gunner|Super':{n:1,t:4,tot:70}}})); }""")
    await pg.goto(url)
    try: await pg.wait_for_selector('.vgroup', timeout=8000)
    except Exception: print('NO GROUPS. status:', await pg.inner_text('#status'), errs); await b.close(); return
    await pg.wait_for_timeout(300)
    print('STATUS:', await pg.inner_text('#status'))
    print('TOP:', (await pg.inner_text('#topinfo')).replace('\n', ' | '))
    print('XUR:', (await pg.inner_text('#xurPanel')).replace('\n', ' | ')[:400])
    print('DIAG:', (await pg.text_content('#vDiagBody')).replace('\n',' | ')[:500])
    print('CORE:', (await pg.inner_text('#corePanel')).replace('\n', ' | ')[:700])
    print('GROUPS:', (await pg.inner_text('#groups')).replace('\n', ' | ')[:900])
    print('NAV:', (await pg.inner_text('#vNav')).replace('\n', ' | '))
    print('singular calls:', [c for c in calls if c[0] == 'one'])
    await pg.click('#vNav [data-foldall="1"]'); await pg.wait_for_timeout(100)
    print('folded:', await pg.eval_on_selector_all('#groups details.vgroup', 'els => els.map(e => e.open)'), localStorage_fold := await pg.evaluate("localStorage.getItem('vendFold')"))
    await pg.click('#vNav a[data-jump^="vg-"]'); await pg.wait_for_timeout(400)
    print('after jump:', await pg.eval_on_selector_all('#groups details.vgroup', 'els => els.map(e => e.open)'))
    await pg.click('#vNav [data-foldall="0"]'); await pg.wait_for_timeout(100)
    print('xur fold:', await pg.eval_on_selector('#vg-xur', 'e => e.open'), (await pg.inner_text('#vg-xur > summary')).replace('\n',' | '))
    await pg.click('#vg-xur > summary'); await pg.wait_for_timeout(100)
    print('xur after click:', await pg.eval_on_selector('#vg-xur', 'e => e.open'), await pg.evaluate("localStorage.getItem('vendFold')"))
    await pg.click('#vNav a[data-jump="vg-xur"]'); await pg.wait_for_timeout(300)
    print('xur after jump:', await pg.eval_on_selector('#vg-xur', 'e => e.open'))
    print('core folds:', await pg.eval_on_selector_all('#corePanel details.corebox', 'els => els.map(e => e.open)'))
    await pg.hover('#corePanel .vrollhit[data-roll]'); await pg.wait_for_timeout(900)
    print('swap buttons:', await pg.eval_on_selector_all('#rollPop [data-swap]', 'els => els.length'), 'alts:', await pg.eval_on_selector_all('#rollPop .rp-alt', 'els => els.map(e => e.title)'))
    print('ROLLPOP:', (await pg.inner_text('#rollPop')).replace('\n', ' | ')[:300], '| hidden:', await pg.eval_on_selector('#rollPop', 'e => e.classList.contains("hidden")'))
    await pg.mouse.move(5, 5); await pg.wait_for_timeout(500)
    print('skip tiles:', await pg.eval_on_selector_all('.skipt', 'els => els.length'))
    await pg.uncheck('#hideCipher'); await pg.wait_for_timeout(100)
    print('XUR shown:', (await pg.inner_text('#xurPanel')).replace('\n', ' | ')[:400])
    await pg.screenshot(path='vendors.png', full_page=True)
    print('vendor calls:', [c for c in calls if c[0] == 'vendors'])
    # a new armor drop shows up in the stream on the vendors page, and can be pulled from there
    CH.append({"itemHash": A, "itemInstanceId": "a9", "state": 0, "bucketHash": 215593132})
    await pg.click('#btnRefresh2'); await pg.wait_for_timeout(1200)
    await pg.click('#btnStream'); await pg.wait_for_timeout(200)
    print('STREAM:', (await pg.inner_text('#streamList')).replace('\n', ' | ')[:300])
    print('links:', await pg.eval_on_selector_all('#streamList a', 'els => els.map(e => e.getAttribute("href"))'))
    calls.clear()
    await pg.click('[data-sact=pull]'); await pg.wait_for_timeout(1500)
    for c in calls: print('CALL', c)
    print('after pull:', (await pg.inner_text('#streamList')).replace('\n', ' | ')[:160])
    print('status:', await pg.inner_text('#status'))
    # switch to the Titan: vendors load for that character
    calls.clear()
    await pg.click('#vChar .chip:has-text("Titan")'); await pg.wait_for_timeout(1200)
    print('titan calls:', [c for c in calls if c[0] == 'vendors'])
    # the stream link opens the drop on the Armor page, and the drop gets its verdict there
    await pg.goto('file:///home/claude/godroll-checker/armor.html#open=a9'); await pg.wait_for_timeout(2500)
    print('armor detail open:', await pg.is_visible('#detail'), '| url:', pg.url.split('/')[-1])
    print('detail:', (await pg.inner_text('#dbody')).replace('\n',' | ')[:120])
    ev = await pg.evaluate("JSON.parse(localStorage.getItem('stream')).filter(e => e.id === 'a9').map(e => e.label + ' / ' + e.extra)")
    print('stream event now:', ev)
    print('errors', errs); await b.close()
asyncio.run(main())
