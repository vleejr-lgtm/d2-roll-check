import json, asyncio
from playwright.async_api import async_playwright
W,H,C,G,S,M=101,102,103,104,105,106
statn={W:"Weapons",H:"Health",C:"Class",G:"Grenade",S:"Super",M:"Melee"}
HELM=3448274439; ARMS=3551918588; CLASSI=1585787867
lite={}
def item(h,name,bucket,cls=0,tier=5): lite[str(h)]={"displayProperties":{"name":name,"icon":"/a.png"},"itemTypeDisplayName":"Helmet","itemType":2,"inventory":{"tierType":tier,"bucketTypeHash":bucket},"classType":cls}
item(1,"Techsec Helm",HELM); item(20,"Reverie Dawn Hood",HELM,2); item(10,"AION Adapter Mask",HELM,1); item(11,"AION Adapter Grips",ARMS,1); item(12,"Orpheus Rig",20886954,1,6); item(13,"Loreley Splendor Helm",HELM,0,6); item(14,"Triumphal Anthem Vest",14239492,1); item(2,"Kepler Helm",HELM); item(3,"Old Legacy Helm",HELM); item(4,"Heart of Inmost Light",ARMS,0,6); item(5,"Exotic Class Bond",CLASSI,0,6)
for h,n,t in [(900,"Gunner","Archetype"),(901,"Bulwark","Archetype"),(950,"Weapons Mod","General Armor Mod"),(960,"Masterwork","Armor Masterwork"),(970,"Health Mod","Helmet Armor Mod"),(971,"Balanced Tuning","Tuning Mod"),(972,"Class Mod","General Armor Mod"),(973,"Hands-On","Helmet Armor Mod"),(980,"Empty Mod Socket","General Armor Mod"),(981,"Empty Mod Socket","Helmet Armor Mod"),(982,"Empty Tuning Socket","Tuning Mod"),(902,"Specialist","Archetype")]:
  lite[str(h)]={"displayProperties":{"name":n},"itemTypeDisplayName":t,"itemType":19}
full={20:{"hash":20,"screenshot":"","sockets":{"socketEntries":[{"singleInitialItemHash":902},{"singleInitialItemHash":980,"reusablePlugSetHash":300},{"singleInitialItemHash":981,"reusablePlugSetHash":301},{"singleInitialItemHash":982,"reusablePlugSetHash":302},{"singleInitialItemHash":960}]}},972:{"displayProperties":{"name":"Class Mod","icon":"/m.png","description":"+10 Class"},"plug":{"energyCost":{"energyCost":3}},"investmentStats":[{"statTypeHash":C,"value":10}]},973:{"displayProperties":{"name":"Hands-On","icon":"/m.png","description":"Super from melee hits"},"plug":{"energyCost":{"energyCost":4}},"investmentStats":[]},980:{"displayProperties":{"name":"Empty Mod Socket","icon":"/m.png"},"investmentStats":[]},981:{"displayProperties":{"name":"Empty Mod Socket","icon":"/m.png"},"investmentStats":[]},982:{"displayProperties":{"name":"Empty Tuning Socket","icon":"/m.png"},"investmentStats":[]},970:{"displayProperties":{"name":"Health Mod","icon":"/m.png"},"plug":{"energyCost":{"energyCost":3}},"investmentStats":[{"statTypeHash":H,"value":10}]},971:{"displayProperties":{"name":"Balanced Tuning","icon":"/m.png"},"plug":{"energyCost":{"energyCost":0}},"investmentStats":[{"statTypeHash":x,"value":1,"isConditionallyActive":True} for x in (W,H,C,G,S,M)]},950:{"investmentStats":[{"statTypeHash":W,"value":10}]},960:{"investmentStats":[{"statTypeHash":G,"value":5},{"statTypeHash":S,"value":5},{"statTypeHash":M,"value":5}]}}
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
add("H1",10,5,{W:30,G:25,S:20},[900]); add("H2",11,4,{W:28,G:24,M:20},[900])
add("OR",12,0,{W:24,H:8,C:2,G:12,S:10,M:9},[])                       # old exotic
add("L1",13,5,{S:30,M:25,G:20},[]); add("L2",13,5,{W:30,G:25,S:20},[900])   # same exotic, different archetypes -> both keep
add("MW",14,5,{W:30,S:25,H:20,C:5,G:5,M:5},[])                       # masterworked Powerhouse, shows 90
add("NM",14,5,{W:30,S:25,H:20},[])
add("RD1",20,5,{H:30,C:30,W:25,M:6,G:6,S:6},[902,970,981,971,960])   # DIM: base 75 + 13 mods + 15 MW = 103
add("RD2",20,5,{C:30,W:25,H:20},[902])
prof={"profileInventory":{"data":{"items":items}},"characters":{"data":{"c1":{"characterId":"c1","classType":0,"light":550,"dateLastPlayed":"2026-11-25T00:00:00Z"}}},
 "characterInventories":{"data":{"c1":{"items":[]}}},"characterEquipment":{"data":{"c1":{"items":[]}}},
 "profilePlugSets":{"data":{"plugs":{"300":[{"plugItemHash":970},{"plugItemHash":972}],"301":[{"plugItemHash":973}],"302":[{"plugItemHash":971}]}}},"itemComponents":{"instances":{"data":inst},"stats":{"data":st},"sockets":{"data":sk}}}
ok=lambda r:{"ErrorCode":1,"Response":r}
calls=[]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page(viewport={'width':1400,'height':1100})
    async def route(rt):
      u=rt.request.url
      if '/Manifest/DestinyStatDefinition/' in u: body=ok({"displayProperties":{"name":statn[int(u.rstrip('/').split('/')[-1])]}})
      elif '/Manifest/DestinyPlugSetDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body=ok({'reusablePlugItems':[{'plugItemHash':x} for x in {'300':[980,970,972,999],'301':[981,973],'302':[982,971]}[h]]})
      elif '/Manifest/DestinyInventoryItemDefinition/' in u: body=ok(full.get(int(u.rstrip('/').split('/')[-1]),{}))
      elif 'Destiny2/Manifest' in u: body=ok({"version":"v9","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/common/lite.json","DestinyEquipableItemSetDefinition":"/common/sets.json"}}})
      elif 'lite.json' in u: body=lite
      elif 'sets.json' in u: body={"77":{"displayProperties":{"name":"Techsec"},"setItems":[1]},"78":{"displayProperties":{"name":"AION Adapter"},"setItems":[10,11]},"79":{"displayProperties":{"name":"Reverie Dawn"},"setItems":[20]}}
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
    await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3}))")
    await pg.reload(); await pg.wait_for_selector('.card', timeout=30000)
    calls.clear()
    await pg.click('.card[data-open="RD1"] .name'); await pg.wait_for_selector('.modslot')
    print('slots:', await pg.eval_on_selector_all('.modslot', "els=>els.map(e=>e.innerText.replace(/\\n/g,' '))"), '|', await pg.inner_text('.energy'))
    await pg.click('.modslot[data-slot="2"]'); await pg.wait_for_selector('.mopt')
    print('helmet options:', await pg.eval_on_selector_all('.mopt b', "els=>els.map(e=>e.innerText)"))
    await pg.click('.mopt[data-mod="973"]')
    await pg.click('.modslot[data-slot="1"]'); await pg.wait_for_selector('.mopt')
    print('general options (999 not unlocked):', await pg.eval_on_selector_all('.mopt b', "els=>els.map(e=>e.innerText)"))
    await pg.click('.mopt[data-mod="972"]')
    print('staged:', await pg.inner_text('.modchanges'), '|', await pg.inner_text('.energy'))
    await pg.screenshot(path='mods.png')
    await pg.click('#mApply'); await pg.wait_for_timeout(4000)
    for c in calls: print('CALL', c[0], c[1].get('plug'), c[1].get('transferToVault'))
    print('errors', errs); await b.close()
asyncio.run(main())
