import json, asyncio
from playwright.async_api import async_playwright
H=3001598094
boss=[839105230,2420895100,1354429876,3966416502]; minor=[839105230,1561002382,684456054,654512643]
defs={str(H):{"displayProperties":{"name":"21% Delirium","icon":"/x.png"},"itemTypeDisplayName":"Machine Gun","itemType":3,"inventory":{"tierType":5}}}
names={839105230:"Arrowhead Brake",2420895100:"Appended Mag",1354429876:"Fourth Time's the Charm",3966416502:"Rolling Storm",1561002382:"Alloy Magazine",684456054:"Light Touch",654512643:"Gear Shift",11:"Reconstruction",12:"One for All",13:"Tier 5: Handling",14:"Tier 1: Stability",15:"Outlaw",16:"Rampage"}
types={839105230:"Barrel",2420895100:"Magazine",1561002382:"Magazine",13:"Masterwork",14:"Masterwork"}
for h,n in names.items(): defs[str(h)]={"displayProperties":{"name":n},"itemTypeDisplayName":types.get(h,"Trait"),"itemType":19}
wl=open('/home/claude/probe/voltron.txt').read()
S=lambda hs:{"sockets":[{"plugHash":h,"isVisible":True} for h in hs]}
items=[{"itemHash":H,"itemInstanceId":x} for x in "abc"]
prof={"profileInventory":{"data":{"items":items}},"characters":{"data":{}},
 "itemComponents":{"instances":{"data":{"a":{"primaryStat":{"value":550}},"b":{"primaryStat":{"value":550}},"c":{"primaryStat":{"value":540}}}},
  "sockets":{"data":{"a":S(boss+[13]),"b":S([839105230,2420895100,11,12,14]),"c":S([15,16,14])}},
  "reusablePlugs":{"data":{"b":{"plugs":{"2":[{"plugItemHash":1354429876}],"3":[{"plugItemHash":3966416502}]}}}}}}
ok=lambda r:{"ErrorCode":1,"Response":r}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page()
    async def route(rt):
      u=rt.request.url
      if 'Manifest' in u: body=ok({"version":"v2","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/common/lite.json"}}})
      elif 'lite.json' in u: body=defs
      elif 'SearchDestinyPlayerByBungieName' in u: body=ok([{"membershipType":3,"membershipId":"42","crossSaveOverride":0}])
      elif '/Profile/' in u: body=ok(prof)
      elif 'voltron' in u: return await rt.fulfill(body=wl, headers={"access-control-allow-origin":"*"})
      elif 'aegis_endgame' in u: return await rt.fulfill(body=open('/home/claude/wl/aegis_endgame_pve_dim_wishlist.txt').read(), headers={"access-control-allow-origin":"*"})
      elif 'monument-pve' in u: return await rt.fulfill(body=open('/home/claude/wl/monument-pve.txt').read(), headers={"access-control-allow-origin":"*"})
      elif 'monument-pvp' in u: return await rt.fulfill(body=open('/home/claude/wl/monument-pvp.txt').read(), headers={"access-control-allow-origin":"*"})
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file:///home/claude/godroll-checker/index.html')
    await pg.fill('#apiKey','k'); await pg.click('#btnSave')
    await pg.fill('#bungieName','Dup#1234'); await pg.click('#btnScan')
    await pg.wait_for_selector('.card', timeout=60000)
    await pg.select_option('#sort','dupes')
    for c in await pg.query_selector_all('.card'): print('---', (await c.inner_text()).split('Community notes')[0].replace('\n',' | ')[:400])
    await pg.screenshot(path='dup.png', full_page=True)
    print('FOOTER:', await pg.inner_text('#sitefoot')); print('NAV:', await pg.eval_on_selector_all('.tabs a', "els=>els.map(e=>e.getAttribute('href'))"))
    print('errors', errs); await b.close()
asyncio.run(main())
