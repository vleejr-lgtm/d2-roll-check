import json, asyncio
from playwright.async_api import async_playwright
lite={}
def d(h,n,t,it,tier=5,b=0,c=3): lite[str(h)]={"displayProperties":{"name":n,"icon":"/i%d.png"%h},"itemTypeDisplayName":t,"itemType":it,"inventory":{"tierType":tier,"bucketTypeHash":b},"classType":c}
d(1,"Fatebringer","Hand Cannon",3,5,1498876634); d(2,"Gjallarhorn","Rocket Launcher",3,6); d(3,"Techsec Helm","Helmet",2,5,3448274439,0); d(4,"Enhancement Core","Material",9,3)
d(5,"Gilded Sunrise","Shader",19,5); d(6,"Dawnblade","Subclass",16); d(7,"Some Bounty","Bounty",26,2); d(8,"Exotic Engram","Engram",8,6); d(9,"Sparrow X","Vehicle",22,5); d(11,"Old Rare Gun","Auto Rifle",3,4,1498876634); d(12,"Kept Gun","Scout Rifle",3,5,1498876634); d(13,"Lost Gun","Pulse Rifle",3,5,1498876634); d(3159615086,"Glimmer","Currency",1,1); d(2817410917,"Bright Dust","Currency",1,5); d(1022552290,"Legendary Shards","Currency",1,5)
prof={"profileCurrencies":{"data":{"items":[{"itemHash":3159615086,"quantity":481558},{"itemHash":2817410917,"quantity":950},{"itemHash":1022552290,"quantity":0}]}},"profileInventory":{"data":{"items":[{"itemHash":1,"itemInstanceId":"V1","bucketHash":138197802,"state":1},{"itemHash":2,"itemInstanceId":"V2","bucketHash":138197802},{"itemHash":4,"bucketHash":1469714392,"quantity":420},{"itemHash":5,"bucketHash":3313201758,"quantity":3},{"itemHash":9,"itemInstanceId":"V9","bucketHash":138197802}]}},
 "characters":{"data":{"c1":{"characterId":"c1","classType":0,"light":2010,"dateLastPlayed":"2026-11-26T00:00:00Z"},"c2":{"characterId":"c2","classType":2,"light":1990,"dateLastPlayed":"2026-11-20T00:00:00Z"}}},
 "characterInventories":{"data":{"c1":{"items":[{"itemHash":11,"itemInstanceId":"W11","bucketHash":1498876634},{"itemHash":12,"itemInstanceId":"W12","bucketHash":1498876634,"state":1},{"itemHash":13,"itemInstanceId":"PW","bucketHash":215593132},{"itemHash":3,"itemInstanceId":"C3","bucketHash":3448274439},{"itemHash":7,"bucketHash":1345459588},{"itemHash":8,"itemInstanceId":"P8","bucketHash":215593132}]},"c2":{"items":[{"itemHash":1,"itemInstanceId":"C21","bucketHash":1498876634},{"itemHash":4,"bucketHash":375726501,"quantity":1}]}}},
 "characterEquipment":{"data":{"c1":{"items":[{"itemHash":12,"itemInstanceId":"EQK","bucketHash":1498876634},{"itemHash":6,"itemInstanceId":"S6","bucketHash":3284755031},{"itemHash":2,"itemInstanceId":"E2","bucketHash":953998645}]}}},
 "itemComponents":{"instances":{"data":{"V1":{"primaryStat":{"value":550}},"V2":{"primaryStat":{"value":560},"gearTier":5},"C3":{"primaryStat":{"value":540},"gearTier":4},"E2":{"primaryStat":{"value":555}},"C21":{"primaryStat":{"value":530}}}}}}
S={'sw':False}
ok=lambda r:{"ErrorCode":1,"Response":r}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--disable-web-security']); pg=await b.new_page(viewport={'width':1440,'height':1000})
    calls=[]; errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    async def route(rt):
      u=rt.request.url
      if 'Destiny2/Manifest' in u and u.rstrip('/').endswith('Manifest'): body=ok({"version":"v1","jsonWorldComponentContentPaths":{"en":{"DestinyInventoryItemLiteDefinition":"/c/lite.json"}}})
      elif '/c/lite.json' in u: body=lite
      elif '/Item/' in u and '/Profile/' in u:
        calls.append(('item', u.split('/Item/')[1].split('/')[0], u.split('components=')[1]))
        body=ok({"instance":{"data":{"primaryStat":{"value":550},"gearTier":5}},"stats":{"data":{"stats":{"4284893193":{"statHash":4284893193,"value":140},"1240592695":{"statHash":1240592695,"value":62},"155624089":{"statHash":155624089,"value":48}}}},
          "sockets":{"data":{"sockets":[{"plugHash":9010,"isVisible":True},{"plugHash":9001 if not S['sw'] else 9011,"isVisible":True,"isEnabled":True},{"plugHash":9002,"isVisible":True},{"plugHash":9003,"isVisible":True},{"plugHash":9004,"isVisible":True},{"plugHash":9005,"isVisible":True},{"plugHash":9006,"isVisible":False},{"plugHash":9012,"isVisible":True},{"plugHash":9020 if not S.get('mod') else 9031,"isVisible":True}]}},
          "reusablePlugs":{"data":{"plugs":{"1":[{"plugItemHash":9001,"canInsert":True,"enabled":True},{"plugItemHash":9011,"canInsert":True,"enabled":True}],"2":[{"plugItemHash":9002,"canInsert":True},{"plugItemHash":9013,"canInsert":False}]}}}})
      elif '/Manifest/DestinyInventoryItemDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]
        P={"9001":{"displayProperties":{"name":"Arrowhead Brake","icon":"/p1.png","description":"Lightly vented."},"itemTypeDisplayName":"Barrel","plug":{"plugCategoryIdentifier":"barrels"}},
           "9002":{"displayProperties":{"name":"Explosive Payload","icon":"/p2.png"},"itemTypeDisplayName":"Trait","plug":{"plugCategoryIdentifier":"frames"}},
           "9003":{"displayProperties":{"name":"Kill Tracker","icon":"/p3.png"},"itemTypeDisplayName":"Tracker","plug":{"plugCategoryIdentifier":"v400.plugs.weapons.masterworks.trackers"}},
           "9004":{"displayProperties":{"name":"Default Shader","icon":"/p4.png"},"plug":{"plugCategoryIdentifier":"shader"}},
           "9005":{"displayProperties":{"name":"Firefly","icon":"/p5.png"},"itemTypeDisplayName":"Enhanced Trait","plug":{"plugCategoryIdentifier":"frames"}},
           "9006":{"displayProperties":{"name":"Hidden","icon":"/p6.png"},"plug":{"plugCategoryIdentifier":"frames"}},
           "9010":{"displayProperties":{"name":"Adaptive Frame","icon":"/f0.png","description":"140 rpm"},"itemTypeDisplayName":"Intrinsic","plug":{"plugCategoryIdentifier":"intrinsics"}},
           "9011":{"displayProperties":{"name":"Corkscrew Rifling","icon":"/p11.png"},"itemTypeDisplayName":"Barrel","plug":{"plugCategoryIdentifier":"barrels"}},
           "9012":{"displayProperties":{"name":"Masterwork: Range","icon":"/mw.png"},"itemTypeDisplayName":"Masterwork","plug":{"plugCategoryIdentifier":"v400.plugs.weapons.masterworks.stat.range"}},
           "9020":{"displayProperties":{"name":"Empty Mod Socket","icon":"/em.png"},"plug":{"plugCategoryIdentifier":"v400.weapon.mod_empty"}},
           "9030":{"displayProperties":{"name":"Backup Mag","icon":"/bm.png","description":"More ammo."},"itemTypeDisplayName":"Weapon Mod","plug":{"plugCategoryIdentifier":"v400.weapon.mod_magazine","energyCost":{"energyCost":0}}},
           "9031":{"displayProperties":{"name":"Counterbalance Stock","icon":"/cb.png"},"itemTypeDisplayName":"Weapon Mod","plug":{"plugCategoryIdentifier":"v400.weapon.mod_guns"}},
           "9013":{"displayProperties":{"name":"Rampage","icon":"/p13.png"},"itemTypeDisplayName":"Trait","plug":{"plugCategoryIdentifier":"frames"}}}
        body=ok(P.get(h, {"displayProperties":{"name":"Fatebringer","icon":"/f.png"},"itemTypeAndTierDisplayName":"Legendary Hand Cannon","sockets":{"socketEntries":[{},{},{},{},{},{},{},{},{"reusablePlugSetHash":555}]}}))
      elif '/Manifest/DestinyStatDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body=ok({"4284893193":{"displayProperties":{"name":"Rounds Per Minute"}},"1240592695":{"displayProperties":{"name":"Range"}},"155624089":{"displayProperties":{"name":"Stability"}}}.get(h,{}))
      elif '/Manifest/DestinyInventoryBucketDefinition/' in u:
        h=u.rstrip('/').split('/')[-1]; body=ok({'1498876634':{'itemCount':3,'category':3},'138197802':{'itemCount':1300,'displayProperties':{'name':'General'}},'1469714392':{'itemCount':50,'displayProperties':{'name':'Consumables'}},'3313201758':{'itemCount':1,'displayProperties':{'name':'Modifications'}},'375726501':{'itemCount':10,'category':1,'displayProperties':{'name':'Engrams'}}}.get(h,{}))
      elif 'GetMembershipsForCurrentUser' in u: body=ok({"destinyMemberships":[{"membershipType":3,"membershipId":"42"}],"primaryMembershipId":"42"})
      elif '/Profile/' in u and 'components=305' in u and '/Item/' not in u: calls.append(('plugsets','305')); body=ok({"profilePlugSets":{"data":{"plugs":{"555":[{"plugItemHash":9030,"canInsert":True,"enabled":True},{"plugItemHash":9031,"canInsert":True,"enabled":True},{"plugItemHash":9020,"canInsert":True,"enabled":True}]}}}})
      elif '/Profile/' in u: body=ok(prof)
      elif '/Actions/' in u:
        if 'InsertSocketPlugFree' in u:
          pbx=json.loads(rt.request.post_data)
          if pbx['plug']['socketIndex']==8: S['mod']=True
          else: S['sw']=True
        calls.append((u.split('/Actions/Items/')[1], json.loads(rt.request.post_data))); body=ok(0)
      elif u.endswith('.png'): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin":"*","content-type":"application/json"})
    await pg.route('**/*', route)
    url='file:///home/claude/godroll-checker/vault.html'
    await pg.goto(url); await pg.evaluate("localStorage.clear(); localStorage.setItem('apiKey','k')")
    await pg.goto(url); await pg.wait_for_timeout(800)
    print('OUT:', await pg.is_visible('#vSignin'), await pg.inner_text('#status'))
    await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3}))")
    await pg.goto(url); await pg.wait_for_selector('.vit', timeout=15000); await pg.wait_for_timeout(300)
    print('status:', await pg.inner_text('#status'))
    print('space:', (await pg.inner_text('#vSpace')).replace('\n',' | '))
    print('sum:', (await pg.inner_text('#vSum')).replace('\n',' | '))
    print('where:', (await pg.inner_text('#vWhere')).replace('\n',' '), '| what:', (await pg.inner_text('#vKind')).replace('\n',' '))
    print('groups:', await pg.eval_on_selector_all('.vgroup h3', 'e=>e.map(x=>x.innerText)'))
    names=lambda: pg.eval_on_selector_all('.vit .vname', 'e=>e.map(x=>x.innerText)')
    for q in ['hand cannon','exotic','t5','vault rocket','postmaster','locked','zzz']:
      await pg.fill('#vSearch', q); await pg.wait_for_timeout(250); print('search', repr(q), await names())
    await pg.fill('#vSearch',''); await pg.wait_for_timeout(250)
    await pg.click('[data-w="c1"]'); await pg.wait_for_timeout(150); print('c1:', await names())
    await pg.click('[data-k="armor"]'); await pg.wait_for_timeout(150); print('c1 armor:', await names())
    await pg.click('[data-w="all"]'); await pg.click('[data-k="all"]')
    await pg.select_option('#vSort','power'); await pg.wait_for_timeout(150); print('by power:', (await names())[:4])
    await pg.select_option('#vSort','type')
    print('V1 row:', (await pg.inner_text('.vit:has([data-id="V1"])')).replace('\n',' | '))
    await pg.click('[data-act="pull"][data-id="PW"]'); await pg.wait_for_timeout(800)
    print('PW calls:', [(c[0], c[1].get('itemId'), c[1].get('transferToVault')) for c in calls if isinstance(c[1], dict)]); print('PW status:', await pg.inner_text('#status')); calls.clear()
    await pg.click('[data-act="pull"][data-id="V1"]'); await pg.wait_for_timeout(500)
    await pg.click('[data-act="vault"][data-id="C3"]'); await pg.wait_for_timeout(500)
    await pg.click('[data-act="lock"][data-id="V2"]'); await pg.wait_for_timeout(500)
    print('calls:', [(c[0], c[1].get('itemId'), c[1].get('transferToVault'), c[1].get('state'), c[1].get('characterId')) for c in calls if isinstance(c[1], dict)])
    await pg.hover('.vit[data-roll="V1"] .vname'); await pg.wait_for_timeout(900)
    print('ROLL hover:', (await pg.inner_text('#rollPop')).replace('\n',' | '), '| visible:', await pg.is_visible('#rollPop'))
    print('item calls:', [c for c in calls if c[0]=='item'][-1:])
    await pg.hover('#rollPop'); await pg.wait_for_timeout(400); print('still open after moving in:', await pg.is_visible('#rollPop'))
    await pg.click('#rollPop [data-swap*="|9011|"]'); await pg.wait_for_timeout(1200)
    print('swap call:', [ (c[0], c[1].get('plug'), c[1].get('itemId'), c[1].get('characterId')) for c in calls if isinstance(c[1], dict) and 'Insert' in c[0]])
    print('ROLL after swap:', (await pg.inner_text('#rollPop')).replace('\n',' | '))
    await pg.click('#rollPop [data-modpick]'); await pg.wait_for_timeout(800)
    print('MOD list:', (await pg.inner_text('#rollPop .rp-modlist')).replace('\n',' | '))
    await pg.click('#rollPop [data-modset*="|9031|"]'); await pg.wait_for_timeout(1000)
    print('mod call:', [(c[0], c[1].get('plug')) for c in calls if isinstance(c[1], dict) and 'Insert' in c[0]][-1:])
    print('mods after:', await pg.eval_on_selector_all('#rollPop .rp-mod', "e=>e.map(x=>x.getAttribute('title'))"))
    await pg.screenshot(path='/home/claude/tests/roll_swap.png')
    await pg.screenshot(path='/home/claude/tests/roll_vault.png')
    await pg.mouse.move(5,5); await pg.wait_for_timeout(300); print('hidden after leave:', await pg.is_hidden('#rollPop'))
    await pg.evaluate("localStorage.setItem('stream', JSON.stringify([{t:Date.now(), kind:'drop', page:'weapons', id:'V2', name:'Gjallarhorn', icon:'', v:'new', label:'New', extra:''}])); localStorage.setItem('pmMakeRoom','0')")
    await pg.click('#btnStream'); await pg.wait_for_timeout(300)
    n0=len(calls)
    await pg.click('#streamList [data-sact="pull"][data-sid="V2"]'); await pg.wait_for_timeout(800)
    print('STREAM pull calls:', [(c[0], c[1].get('itemId'), c[1].get('transferToVault'), c[1].get('characterId')) for c in calls[n0:] if isinstance(c[1], dict)])
    await pg.evaluate("document.getElementById('stream').classList.add('hidden')")
    print('PM button:', await pg.inner_html('#btnPM'))
    await pg.screenshot(path='/home/claude/tests/vault.png')
    print('nav:', await pg.eval_on_selector_all('header .tabs a', 'e=>e.map(x=>x.textContent+(x.classList.contains("active")?"*":""))'))
    # Inventory follows the active character (last played first), with tabs to switch
    await pg.goto('file:///home/claude/godroll-checker/vault.html'); await pg.wait_for_selector('.invpanel', timeout=15000); await pg.wait_for_timeout(300)
    eng = "() => [...document.querySelectorAll('.invsec')].filter(s => /Engrams/.test(s.textContent)).map(s => s.querySelector('.invhead').textContent)"
    print('INV default:', await pg.eval_on_selector('.invtabs .chip.on', 'e => e.textContent'), await pg.evaluate(eng))
    await pg.click('.invtabs [data-invc="c2"]'); await pg.wait_for_timeout(150)
    print('INV c2:', await pg.eval_on_selector('.invtabs .chip.on', 'e => e.textContent'), await pg.evaluate(eng))
    await pg.click('#vWhere [data-w="c1"]'); await pg.wait_for_timeout(150)
    print('INV where c1:', await pg.eval_on_selector('.invtabs .chip.on', 'e => e.textContent'), await pg.evaluate(eng))
    print('errors', errs); await b.close()
asyncio.run(main())
