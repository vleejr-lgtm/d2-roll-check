import json, asyncio
from playwright.async_api import async_playwright
lite={}
def d(h,n,t,it,tier,b,c=3): lite[str(h)]={"displayProperties":{"name":n,"icon":"/i%d.png"%h},"itemTypeDisplayName":t,"itemType":it,"inventory":{"tierType":tier,"bucketTypeHash":b},"classType":c}
K,E,P,G,H,A,C,L,CL,SUB=1498876634,2465295065,953998645,4023194814,3448274439,3551918588,14239492,20886954,1585787867,3284755031
for i in range(1,11): d(100+i,"Kin %d"%i,"Hand Cannon",3,5 if i!=3 else 4,K)
d(201,"Energy Eq","Pulse Rifle",3,5,E); d(301,"Rocket","Rocket Launcher",3,6,P); d(401,"Ghost Shell","Ghost Shell",24,5,G)
d(501,"Warlock Helm","Helmet",2,5,H,2); d(502,"Vault Helm","Helmet",2,5,H,2); d(503,"Titan Helm","Helmet",2,5,H,0); d(601,"Dawnblade","Subclass",16,5,SUB,2)
d(701,"Vault Gun","Scout Rifle",3,5,K)
inst={}
def it(h,iid,b,st=0,pw=400,gt=0): inst[iid]={"primaryStat":{"value":pw},"gearTier":gt}; return {"itemHash":h,"itemInstanceId":iid,"bucketHash":b,"state":st}
prof={"profile":{"data":{"userInfo":{"bungieGlobalDisplayName":"ElGreeko","bungieGlobalDisplayNameCode":42}}},
 "profileCurrencies":{"data":{"items":[{"itemHash":3159615086,"quantity":1135}]}},
 "profileInventory":{"data":{"items":[it(502,"VH",138197802,pw=410), it(503,"VT",138197802), it(701,"VG",138197802,pw=450,gt=5)]}},
 "characters":{"data":{"w1":{"characterId":"w1","classType":2,"raceType":1,"light":384,"dateLastPlayed":"2026-11-27T00:00:00Z","emblemPath":"/e.png","emblemBackgroundPath":"/eb.png","stats":{"1935470627":384,"2996146975":7,"392767087":2}},
                        "t1":{"characterId":"t1","classType":0,"light":127,"dateLastPlayed":"2026-11-01T00:00:00Z","stats":{}}}},
 "characterEquipment":{"data":{"w1":{"items":[it(101,"K1",K,1,pw=420,gt=5), it(201,"E1",E), it(301,"P1",P), it(401,"G1",G), it(501,"H1",H), it(601,"S1",SUB)]},"t1":{"items":[]}}},
 "characterInventories":{"data":{"w1":{"items":[it(502,"PMH",215593132,pw=405), {"itemHash":3159615086,"bucketHash":215593132,"quantity":5}]+[it(100+i,"K%d"%i,K,st=1 if i in (2,4,5,6,7,8,9) else 0,pw=300+i,gt=3) for i in range(2,11)]},"t1":{"items":[]}}},
 "itemComponents":{"instances":{"data":inst}}}
ok=lambda r:{"ErrorCode":1,"Response":r}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page(viewport={'width':1440,'height':1100})
    calls=[]; errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    async def route(rt):
      u=rt.request.url
      if '/Manifest/DestinyStatDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body=ok({"2996146975":{"displayProperties":{"name":"Weapons"}},"392767087":{"displayProperties":{"name":"Health"}}}.get(h,{}))
      elif '/Manifest/DestinyInventoryBucketDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body=ok({str(K):{"itemCount":10,"category":3}}.get(h,{"itemCount":10,"category":3}))
      elif 'Destiny2/Manifest' in u: body=ok({"version":"v1","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/c/lite.json"}}})
      elif '/c/lite.json' in u: body=lite
      elif 'GetMembershipsForCurrentUser' in u: body=ok({"destinyMemberships":[{"membershipType":3,"membershipId":"42"}],"primaryMembershipId":"42"})
      elif '/Profile/' in u: calls.append(('profile', u.split('components=')[1])); body=ok(prof)
      elif '/Actions/' in u: pb=json.loads(rt.request.post_data); calls.append((u.split('/Actions/Items/')[1].strip('/'), pb.get('itemId'), pb.get('transferToVault'), pb.get('characterId'))); body=ok(0)
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    url='file:///home/claude/godroll-checker/character.html'
    await pg.goto(url); await pg.evaluate("localStorage.clear(); localStorage.setItem('apiKey','k'); localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3})); localStorage.setItem('verdicts:weapons', JSON.stringify({at:Date.now()-300000, m:{K1:['god','Matches a recommended roll (PvE)','1/3',0], K2:['trash','Has none of the recommended perk combos','3/3',0], K3:['close','Has 2 of 4 perks','',0], K4:['unrated','','',1], P1:['exotic','Exotic','',0]}})); localStorage.setItem('verdicts:armor', JSON.stringify({at:Date.now()-3600000, m:{H1:['keep','',0,0], VH:['legacy','Old armor (pre Edge of Fate): no archetype or tier.',1,0], PMH:['trash','Dismantle this one.',0,0]}}))")
    await pg.goto(url); await pg.wait_for_selector('.ctile', timeout=15000); await pg.wait_for_timeout(400)
    print('tabs:', (await pg.inner_text('#cTabs')).replace('\n',' | '))
    await pg.drag_and_drop('[data-item="K3"]', '[data-vtab]'); await pg.wait_for_timeout(700)
    await pg.drag_and_drop('[data-item="K5"]', '#cTabs [data-c="t1"]'); await pg.wait_for_timeout(900)
    print('calls:', [c for c in calls if c[0]!='profile'])
    print('warlock kinetic now:', await pg.eval_on_selector_all('.cslot:nth-child(2) [data-item]', 'e=>e.map(x=>x.dataset.item)'))
    print('lastScan:', await pg.inner_text('#lastScan'))
    await pg.click('[data-vtab]'); await pg.wait_for_timeout(300); print('mode after vault tab click:', await pg.evaluate('mode'), await pg.locator('.dvault').count())
    await pg.screenshot(path='/home/claude/tests/character_one.png', full_page=True)
    print('errors', errs); await b.close()
asyncio.run(main())
