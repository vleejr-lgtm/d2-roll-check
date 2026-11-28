import json, asyncio
from playwright.async_api import async_playwright
OPEN_DRAWERS = "new MutationObserver(() => document.querySelectorAll('details.drawer:not([open]), details.tagpop:not([open])').forEach(d => d.open = true)).observe(document, { subtree: true, childList: true });"

H=437854391
defs={str(H):{"displayProperties":{"name":"Action Item","icon":"/x.png"},"itemTypeDisplayName":"Trace Rifle","itemType":3,"inventory":{"tierType":5}},
 "555":{"displayProperties":{"name":"Junk Gun","icon":"/x.png"},"itemTypeDisplayName":"Hand Cannon","itemType":3,"inventory":{"tierType":5}},
 "777":{"displayProperties":{"name":"Big Exotic","icon":"/x.png"},"itemTypeDisplayName":"Auto Rifle","itemType":3,"inventory":{"tierType":6}}}
for h,n,t in [(1840239774,"Fluted Barrel","Barrel"),(732557052,"Tactical Battery","Battery"),(1955165503,"Rimestealer","Trait"),(2922950962,"Enhanced Headstone","Enhanced Trait"),(1,"Outlaw","Trait"),(2,"Shader X","Shader")]:
  defs[str(h)]={"displayProperties":{"name":n},"itemTypeDisplayName":t,"itemType":19}
wl=open('/home/claude/probe/voltron.txt').read()
wl=wl.replace("2922950962","2922950962",1)
prof={"profileInventory":{"data":{"items":[{"itemHash":H,"itemInstanceId":"a"},{"itemHash":555,"itemInstanceId":"b"}]}},
 "characters":{"data":{"c1":{"classType":1}}},"characterInventories":{"data":{"c1":{"items":[{"itemHash":H,"itemInstanceId":"c"}]}}},
 "characterEquipment":{"data":{"c1":{"items":[{"itemHash":777,"itemInstanceId":"d"}]}}},
 "itemComponents":{"sockets":{"data":{"a":{"sockets":[{"plugHash":1840239774,"isVisible":True},{"plugHash":732557052,"isVisible":True},{"plugHash":1955165503,"isVisible":True},{"plugHash":2922950962,"isVisible":True},{"plugHash":2,"isVisible":True}]},
   "c":{"sockets":[{"plugHash":1840239774},{"plugHash":1}]},"b":{"sockets":[{"plugHash":1}]}}},
  "reusablePlugs":{"data":{"c":{"plugs":{"2":[{"plugItemHash":732557052}]}}}}}}
def ok(r): return {"ErrorCode":1,"Response":r}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); ctx=await b.new_context(permissions=['clipboard-read','clipboard-write']); pg=await ctx.new_page(); await pg.add_init_script(OPEN_DRAWERS)
    async def route(rt):
      u=rt.request.url
      if 'Manifest' in u: body=ok({"version":"v1","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/common/lite.json"}}})
      elif 'lite.json' in u: body=defs
      elif 'SearchDestinyPlayer' in u: body=ok([{"membershipType":3,"membershipId":"42","crossSaveOverride":0}])
      elif '/Profile/' in u: body=ok(prof)
      elif 'voltron' in u: return await rt.fulfill(body=wl, headers={"access-control-allow-origin":"*"})
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file:///home/claude/godroll-checker/index.html')
    await pg.fill('#apiKey','k'); await pg.click('#btnSave')
    await pg.fill('#bungieName','Test#1234'); await pg.click('#btnScan')
    try:
      await pg.wait_for_selector('.card', timeout=20000)
    except Exception:
      print('STATUS:', await pg.inner_text('#status'), errs); raise
    print(await pg.inner_text('#status'))
    for c in await pg.query_selector_all('.card'): print('---', (await c.inner_text()).replace('\n',' | ')[:220])
    await pg.select_option('#tagClose','keep')
    async with pg.expect_download() as dl: await pg.click('#btnCsv')
    d=await dl.value; print('CSV', d.suggested_filename); print(open(await d.path()).read())
    await pg.click('#btnSearch'); print('CLIP', await pg.evaluate('navigator.clipboard.readText()'))
    await pg.click('.card [data-copy]'); print('CLIP1', await pg.evaluate('navigator.clipboard.readText()'))
    await pg.screenshot(path='scan.png', full_page=True)
    await pg.click('.tab[data-view=lookup]'); await pg.fill('#lookupText','action'); await pg.wait_for_selector('.lookup-item'); await pg.click('.lookup-item')
    print('lookup rolls:', len(await pg.query_selector_all('.roll')))
    print('errors', errs); await b.close()
asyncio.run(main())
