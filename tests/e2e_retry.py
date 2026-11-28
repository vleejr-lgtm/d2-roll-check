import json, asyncio
from playwright.async_api import async_playwright
OPEN_DRAWERS = "new MutationObserver(() => document.querySelectorAll('details.drawer:not([open]), details.tagpop:not([open])').forEach(d => d.open = true)).observe(document, { subtree: true, childList: true });"
H=3001598094
BAR,MAG,FT,RS,REC,OFA,ARROW2,ALLOY=839105230,2420895100,1354429876,3966416502,11,12,555001,1561002382
names={BAR:"Arrowhead Brake",MAG:"Appended Mag",FT:"Fourth Time's the Charm",RS:"Rolling Storm",REC:"Reconstruction",OFA:"One for All",ARROW2:"Fluted Barrel",ALLOY:"Alloy Magazine",13:"Tier 5: Handling",14:"Tier 1: Stability",900:"Rapid-Fire Frame",15:"Outlaw",16:"Rampage"}
types={BAR:"Barrel",ARROW2:"Barrel",MAG:"Magazine",ALLOY:"Magazine",13:"Masterwork",14:"Masterwork",900:"Intrinsic"}
STAB,HAND,RPM=155624089,943549884,4284893193
inv={BAR:[(STAB,6)],ARROW2:[(STAB,6),(HAND,16)],MAG:[],ALLOY:[],13:[(HAND,10)],14:[(STAB,2)]}
lite={str(H):{"displayProperties":{"name":"21% Delirium","icon":"/x.png"},"itemTypeDisplayName":"Machine Gun","itemType":3,"inventory":{"tierType":5}}}
full={}
for h,n in names.items():
  lite[str(h)]={"displayProperties":{"name":n,"icon":"/p.png"},"itemTypeDisplayName":types.get(h,"Trait"),"itemType":19}
  full[h]={"hash":h,"displayProperties":{"name":n,"icon":"/p.png","description":n+" description."},"itemTypeDisplayName":types.get(h,"Trait"),"investmentStats":[{"statTypeHash":a,"value":b,"isConditionallyActive":False} for a,b in inv.get(h,[])]}
full[H]={"hash":H,"displayProperties":{"name":"21% Delirium","icon":"/x.png"},"itemTypeDisplayName":"Machine Gun","screenshot":"/shot.jpg",
 "investmentStats":[{"statTypeHash":STAB,"value":40,"isConditionallyActive":False},{"statTypeHash":HAND,"value":50,"isConditionallyActive":False}],
 "stats":{"statGroupHash":77,"stats":{str(RPM):{"value":900}}},
 "sockets":{"socketEntries":[{"singleInitialItemHash":900},{"randomizedPlugSetHash":501},{"randomizedPlugSetHash":502},{"randomizedPlugSetHash":503},{"randomizedPlugSetHash":504},{"singleInitialItemHash":13}],
  "socketCategories":[{"socketCategoryHash":3956125808,"socketIndexes":[0]},{"socketCategoryHash":4241085061,"socketIndexes":[1,2,3,4]}]}}
plugsets={501:[BAR,ARROW2],502:[MAG,ALLOY],503:[FT,REC,15],504:[RS,OFA,16]}
statgroup={"scaledStats":[{"statHash":STAB,"maximumValue":100,"displayInterpolation":[{"value":0,"weight":0},{"value":100,"weight":100}]},
 {"statHash":HAND,"maximumValue":100,"displayInterpolation":[{"value":0,"weight":0},{"value":100,"weight":100}]},{"statHash":RPM,"maximumValue":1000,"displayAsNumeric":True,"displayInterpolation":[]}]}
statdefs={STAB:"Stability",HAND:"Handling",RPM:"Rounds Per Minute"}
wl=open('/home/claude/probe/voltron.txt').read()
S=lambda hs:{"sockets":[{"plugHash":h,"isVisible":True} for h in hs]}
items=[{"itemHash":H,"itemInstanceId":"a","state":0},{"itemHash":H,"itemInstanceId":"b","state":1}]
prof={"profileInventory":{"data":{"items":items}},"characters":{"data":{"c1":{"characterId":"c1","classType":1,"light":550,"dateLastPlayed":"2026-11-25T00:00:00Z"}}},
 "characterInventories":{"data":{"c1":{"items":[]}}},"characterEquipment":{"data":{"c1":{"items":[]}}},
 "itemComponents":{"instances":{"data":{"a":{"primaryStat":{"value":550}},"b":{"primaryStat":{"value":550}}}},
  "sockets":{"data":{"a":S([900,BAR,MAG,FT,RS,13]),"b":S([900,BAR,MAG,REC,OFA,14])}},
  "reusablePlugs":{"data":{"b":{"plugs":{"3":[{"plugItemHash":REC},{"plugItemHash":FT}],"4":[{"plugItemHash":OFA},{"plugItemHash":RS}]}}}}}}
ok=lambda r:{"ErrorCode":1,"Response":r}
calls=[]
fails={'n':0}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page(viewport={'width':1400,'height':1000}); await pg.add_init_script(OPEN_DRAWERS)
    async def route(rt):
      u=rt.request.url; m=rt.request.method
      if '/Manifest/DestinyInventoryItemDefinition/' in u and fails['n']<1:
        fails['n']+=1; body={"ErrorCode":2107,"ErrorStatus":"OriginHeaderDoesNotMatchKey","Message":"Origin header does not match the provided API key."}
      elif '/Manifest/DestinyInventoryItemDefinition/' in u: body=ok(full[int(u.rstrip('/').split('/')[-1])])
      elif '/Manifest/DestinyPlugSetDefinition/' in u: body=ok({"reusablePlugItems":[{"plugItemHash":h,"currentlyCanRoll":True} for h in plugsets[int(u.rstrip('/').split('/')[-1])]]})
      elif '/Manifest/DestinyStatGroupDefinition/' in u: body=ok(statgroup)
      elif '/Manifest/DestinyStatDefinition/' in u:
        h=int(u.rstrip('/').split('/')[-1]); body=ok({"displayProperties":{"name":statdefs.get(h,"")}})
      elif 'Destiny2/Manifest' in u: body=ok({"version":"v3","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/common/lite.json"}}})
      elif 'lite.json' in u: body=lite
      elif 'OAuth/Token' in u: calls.append(('token',rt.request.post_data)); body={"access_token":"TOK","expires_in":3600,"membership_id":"99"}
      elif 'GetMembershipsForCurrentUser' in u: calls.append(('me',rt.request.headers.get('authorization'))); body=ok({"destinyMemberships":[{"membershipType":3,"membershipId":"42"}],"primaryMembershipId":"42"})
      elif 'SearchDestinyPlayerByBungieName' in u: body=ok([{"membershipType":3,"membershipId":"42","crossSaveOverride":0}])
      elif '/Profile/' in u: body=ok(prof)
      elif '/Actions/' in u: calls.append((u.split('/Actions/')[1], json.loads(rt.request.post_data))); body=ok(0)
      elif 'voltron' in u: return await rt.fulfill(body=wl, headers={"access-control-allow-origin":"*"})
      elif 'raw.githubusercontent' in u: return await rt.fulfill(body="", headers={"access-control-allow-origin":"*"})
      elif u.endswith(('.png','.jpg')): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    url='file:///home/claude/godroll-checker/index.html'
    await pg.goto(url)
    await pg.evaluate("localStorage.setItem('wlPresets', JSON.stringify({aegis:false,gigpve:false,gigpvp:false}))")
    await pg.fill('#apiKey','k'); await pg.fill('#clientId','12345'); await pg.click('#btnSave')
    await pg.fill('#bungieName','Dup#1234'); await pg.click('#btnScan')
    await pg.wait_for_selector('.card', timeout=60000)
    print('needauth hidden before sign-in:', await pg.locator('.card [data-act=lock]').first.is_visible())
    # open detail for copy b
    await pg.click('.card[data-open="b"] .name')
    await pg.wait_for_selector('.perk-o', timeout=20000)
    st=lambda: pg.eval_on_selector_all('.srow', "els=>els.map(e=>e.innerText.replace(/\\n/g,' '))")
    print('stats before:', await st())
    print('columns:', await pg.eval_on_selector_all('.pcol', "els=>els.map(e=>e.querySelectorAll('.perk-o').length)"))
    await pg.hover(f'.perk-o[data-plug="{ARROW2}"]'); print('tooltip:', (await pg.inner_text('#dtip')).replace('\n',' | '))
    await pg.click(f'.perk-o[data-plug="{ARROW2}"]'); await pg.click(f'.perk-o[data-plug="{FT}"]'); await pg.click(f'.perk-o[data-plug="{RS}"]')
    print('stats preview:', await st())
    print('notOwned note:', await pg.locator('.dpanel .swapnote').inner_text() if await pg.locator('.dpanel .swapnote').count() else None)
    await pg.screenshot(path='detail.png')
    await pg.click('#dSave'); await pg.click('#dClose')
    print('cards after save:', [ (await c.inner_text()).split('\n')[:6] for c in await pg.query_selector_all('.card')])
    # simulate Bungie redirect back with code
    await pg.evaluate("sessionStorage.setItem('oauthState','xyz')")
    await pg.goto(url+'?code=CODE1&state=xyz')
    await pg.wait_for_selector('.card', timeout=60000); await pg.wait_for_timeout(500)
    print('auth status:', await pg.inner_text('#authStatus'), '| url:', pg.url.split('/')[-1])
    print('lock btn visible after sign-in:', await pg.locator('.card [data-act=lock]').first.is_visible())
    await pg.click('.card[data-open="b"] .name'); await pg.wait_for_selector('.perk-o')
    await pg.click(f'.perk-o[data-plug="{FT}"]'); await pg.click(f'.perk-o[data-plug="{RS}"]')
    await pg.click('#dApply'); await pg.wait_for_timeout(3000)
    await pg.click('#dLock'); await pg.wait_for_timeout(300); await pg.click('#dClose')
    await pg.click('#btnLockGod'); await pg.wait_for_timeout(1500)
    for c in calls: print('CALL', c)
    print('status:', await pg.inner_text('#status'))
    await pg.screenshot(path='cards_auth.png', full_page=True)
    print('errors', errs); await b.close()
asyncio.run(main())
