import json, asyncio
from playwright.async_api import async_playwright
OPEN_DRAWERS = "new MutationObserver(() => document.querySelectorAll('details.drawer:not([open]), details.tagpop:not([open])').forEach(d => d.open = true)).observe(document, { subtree: true, childList: true });"
W,H,C,G,S,M=101,102,103,104,105,106
statn={W:"Weapons",H:"Health",C:"Class",G:"Grenade",S:"Super",M:"Melee"}
HELM=3448274439; ARMS=3551918588; CLASSI=1585787867
lite={}
def item(h,name,bucket,cls=0,tier=5): lite[str(h)]={"displayProperties":{"name":name,"icon":"/a.png"},"itemTypeDisplayName":"Helmet","itemType":2,"inventory":{"tierType":tier,"bucketTypeHash":bucket},"classType":cls}
item(1,"Techsec Helm",HELM); item(2,"Kepler Helm",HELM); item(3,"Old Legacy Helm",HELM); item(4,"Heart of Inmost Light",ARMS,0,6); item(5,"Exotic Class Bond",CLASSI,0,6)
for h,n,t in [(900,"Gunner","Archetype"),(901,"Bulwark","Archetype"),(950,"Weapons Mod","General Armor Mod"),(960,"Masterwork","Armor Masterwork")]:
  lite[str(h)]={"displayProperties":{"name":n},"itemTypeDisplayName":t,"itemType":19}
full={950:{"investmentStats":[{"statTypeHash":W,"value":10}]},960:{"investmentStats":[{"statTypeHash":G,"value":5},{"statTypeHash":S,"value":5},{"statTypeHash":M,"value":5}]}}
def stats(d): return {"stats":{str(k):{"statHash":k,"value":v} for k,v in d.items()}}
def sock(*h): return {"sockets":[{"plugHash":x} for x in h]}
items=[];inst={};st={};sk={}
def add(iid,h,tier,s,plugs,locked=False):
  items.append({"itemHash":h,"itemInstanceId":iid,"state":1 if locked else 0}); inst[iid]={"primaryStat":{"value":550},**({"gearTier":tier} if tier else {})}; st[iid]=stats(s); sk[iid]=sock(*plugs)
add("A",1,5,{W:40,G:25,S:20},[900,950])                 # T5 Gunner +Super, with a +10 Weapons mod
add("B",2,3,{W:28,G:22,S:16},[900])                     # T3 Gunner +Super -> duplicate of A
add("Bl",2,3,{W:27,G:22,S:16},[900],locked=True)        # locked duplicate -> kept
add("C",2,1,{W:25,G:20,M:10},[900])                     # T1 Gunner +Melee -> outclassed by A
add("D",2,2,{H:26,C:22,W:12},[901])                     # T2 Bulwark -> keep
add("E",3,0,{W:20,H:18,C:15,G:12,S:10,M:15},[])         # legacy
add("X1",4,5,{W:30,G:25,S:20},[900]); add("X2",4,3,{W:25,G:22,S:18},[900])  # exotic dupes
add("CI",5,5,{H:30,C:25,W:20},[901])
prof={"profileInventory":{"data":{"items":items}},"characters":{"data":{"c1":{"characterId":"c1","classType":0,"light":550,"dateLastPlayed":"2026-11-25T00:00:00Z"}}},
 "characterInventories":{"data":{"c1":{"items":[]}}},"characterEquipment":{"data":{"c1":{"items":[]}}},
 "itemComponents":{"instances":{"data":inst},"stats":{"data":st},"sockets":{"data":sk}}}
ok=lambda r:{"ErrorCode":1,"Response":r}
calls=[]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page(viewport={'width':1400,'height':1100}); await pg.add_init_script(OPEN_DRAWERS)
    async def route(rt):
      u=rt.request.url
      if '/Manifest/DestinyStatDefinition/' in u: body=ok({"displayProperties":{"name":statn[int(u.rstrip('/').split('/')[-1])]}})
      elif '/Manifest/DestinyInventoryItemDefinition/' in u: body=ok(full.get(int(u.rstrip('/').split('/')[-1]),{}))
      elif 'Destiny2/Manifest' in u: body=ok({"version":"v9","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/common/lite.json","DestinyEquipableItemSetDefinition":"/common/sets.json"}}})
      elif 'lite.json' in u: body=lite
      elif 'sets.json' in u: body={"77":{"displayProperties":{"name":"Techsec"},"setItems":[1]}}
      elif 'GetMembershipsForCurrentUser' in u: body=ok({'destinyMemberships':[{'membershipType':3,'membershipId':'42'}],'primaryMembershipId':'42'})
      elif 'SearchDestinyPlayerByBungieName' in u: body=ok([{"membershipType":3,"membershipId":"42","crossSaveOverride":0}])
      elif '/Profile/' in u: body=ok(prof)
      elif '/Actions/' in u: calls.append((u.split('/Actions/')[1], json.loads(rt.request.post_data))); body=ok(0)
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file:///home/claude/godroll-checker/armor.html')
    await pg.evaluate("localStorage.setItem('apiKey','k')")
    await pg.fill('#bungieName','Dup#1234'); await pg.click('#btnScan')
    await pg.wait_for_selector('.card', timeout=30000)
    print('status:', await pg.inner_text('#status'))
    for c in await pg.query_selector_all('.card'):
      t=(await c.inner_text()).split('\n'); print('--', ' | '.join(t[:7])[:230])
    print('footer:', (await pg.inner_text('#sitefoot'))[:160])
    # sign in (fake token) and bulk lock keepers
    await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3}))")
    await pg.reload(); await pg.wait_for_selector('.card', timeout=30000)
    await pg.click('#btnLockKeep'); await pg.wait_for_timeout(2500)
    print('lock calls:', [c[1]['itemId'] for c in calls])
    async with pg.expect_download() as dl: await pg.click('#btnCsv')
    d=await dl.value; print(open(await d.path()).read())
    await pg.screenshot(path='armor.png', full_page=True)
    print('errors', errs); await b.close()
asyncio.run(main())
