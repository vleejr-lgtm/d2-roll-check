import json, asyncio, datetime
from playwright.async_api import async_playwright
RAID, NF, NF2, LS, PVP, GM, LSX, LSM = 101, 102, 103, 104, 105, 106, 107, 108
M_CHAMP = 203
EXO = 602
M_SHIELD, M_HIDDEN = 201, 202
MODE_RAID, MODE_STRIKE = 301, 302
MS_NF, MS_RAID, MS_EVT = 401, 402, 403
OBJ1, OBJ2 = 501, 502
ENGRAM = 601
end = (datetime.datetime.utcnow() + datetime.timedelta(days=4)).strftime('%Y-%m-%dT17:00:00Z')
tables = {
  'act': {
    str(RAID): {"displayProperties": {"name": "Salvation's Edge", "description": "Raid desc"}, "originalDisplayProperties": {"name": "Raid: Salvation's Edge (Standard)"}, "pgcrImage": "/r.jpg", "destinationHash": 701, "directActivityModeHash": MODE_RAID, "activityLightLevel": 1990},
    str(NF): {"displayProperties": {"name": "Nightfall: The Glassway", "description": "Strike desc"}, "pgcrImage": "/n.jpg", "destinationHash": 702, "directActivityModeHash": MODE_STRIKE, "activityLightLevel": 2000},
    str(NF2): {"displayProperties": {"name": "Nightfall: The Glassway", "description": "Strike desc"}, "pgcrImage": "/n.jpg", "destinationHash": 702, "directActivityModeHash": MODE_STRIKE, "activityLightLevel": 2020},
    str(LS): {"displayProperties": {"name": "Lost Sector: Bunker E15", "description": "LS desc"}, "pgcrImage": "/l.jpg", "destinationHash": 702},
    str(PVP): {"displayProperties": {"name": "Control"}, "isPvP": True},
    str(GM): {"displayProperties": {"name": ""}},
    str(LSX): {"displayProperties": {"name": "The Conflux: Expert", "description": "Daily lost sector"}, "originalDisplayProperties": {"name": "Lost Sector: The Conflux (Expert)"}, "pgcrImage": "/c.jpg", "destinationHash": 701, "activityLightLevel": 1980},
    "120": {"displayProperties": {"name": "Aphelion's Rest: Expert", "description": "Solo op"}, "pgcrImage": "/a.jpg", "destinationHash": 702, "activityTypeHash": 909, "activityLightLevel": 1980},
    str(LSM): {"displayProperties": {"name": "The Conflux: Master"}, "originalDisplayProperties": {"name": "Lost Sector: The Conflux (Master)"}, "pgcrImage": "/c.jpg", "destinationHash": 701, "activityLightLevel": 2010},
  },
  'mod_': None,
  'mod': {str(M_SHIELD): {"displayProperties": {"name": "Arc Threat", "description": "Arc shields"}, "displayInActivitySelection": True},
          str(M_HIDDEN): {"displayProperties": {"name": "Hidden"}, "displayInActivitySelection": False},
          str(M_CHAMP): {"displayProperties": {"name": "Champion Foes", "description": "Barrier and Overload champions"}, "displayInActivitySelection": True}},
  'mode': {str(MODE_RAID): {"displayProperties": {"name": "Raid"}}, str(MODE_STRIKE): {"displayProperties": {"name": "Strike"}}},
  'ms': {str(MS_NF): {"displayProperties": {"name": "Nightfall", "description": "Weekly Nightfall"}},
         str(MS_RAID): {"displayProperties": {"name": "Featured Raid"}},
         str(MS_EVT): {"displayProperties": {"name": "Iron Banner", "description": "Event is live"}, "image": "/ib.jpg"}},
  'dest': {"701": {"displayProperties": {"name": "Pale Heart"}, "placeHash": 801}, "702": {"displayProperties": {"name": "Europa"}, "placeHash": 802}},
  'atype': {"909": {"displayProperties": {"name": "Lost Sector"}}},
  'place': {"801": {"displayProperties": {"name": "The Traveler"}}, "802": {"displayProperties": {"name": "Europa"}}},
}
paths = {"DestinyInventoryItemLiteDefinition": "/c/lite.json", "DestinyActivityDefinition": "/c/act.json", "DestinyActivityModifierDefinition": "/c/mod.json",
         "DestinyActivityModeDefinition": "/c/mode.json", "DestinyMilestoneDefinition": "/c/ms.json", "DestinyDestinationDefinition": "/c/dest.json", "DestinyPlaceDefinition": "/c/place.json", "DestinyActivityTypeDefinition": "/c/atype.json"}
lite = {str(ENGRAM): {"displayProperties": {"name": "Pinnacle Engram", "icon": "/e.png"}, "itemType": 8}, str(EXO): {"displayProperties": {"name": "Exotic Leg Armor", "icon": "/x.png"}, "itemType": 2}}
pub = {str(MS_NF): {"milestoneHash": MS_NF, "endDate": end, "order": 1, "activities": [{"activityHash": NF, "modifierHashes": [M_SHIELD, M_HIDDEN], "challengeObjectiveHashes": [OBJ1]}, {"activityHash": NF2, "modifierHashes": [M_SHIELD]}]},
       str(MS_RAID): {"milestoneHash": MS_RAID, "endDate": end, "order": 2, "activities": [{"activityHash": RAID, "modifierHashes": [], "challengeObjectiveHashes": [OBJ2]}]},
       str(MS_EVT): {"milestoneHash": MS_EVT, "endDate": end, "order": 3}}
ch = lambda h, p, c, done: {"objective": {"objectiveHash": h, "progress": p, "completionValue": c, "complete": done}}
avail = [
  {"activityHash": NF, "isVisible": True, "isFocusedActivity": True, "recommendedLight": 2000, "modifierHashes": [M_SHIELD], "visibleRewards": [{"rewardItems": [{"itemQuantity": {"itemHash": ENGRAM, "quantity": 1}}]}]},
  {"activityHash": NF2, "isVisible": True, "recommendedLight": 2020},
  {"activityHash": RAID, "isVisible": True, "challenges": [ch(OBJ2, 0, 1, False)]},
  {"activityHash": LS, "isVisible": True, "challenges": [ch(OBJ1, 3, 3, True)], "isCompleted": True},
  {"activityHash": PVP, "isVisible": True},
  {"activityHash": GM, "isVisible": True},
  {"activityHash": LSX, "isVisible": True, "recommendedLight": 1980, "modifierHashes": [M_CHAMP, M_SHIELD], "visibleRewards": [{"rewardItems": [{"itemQuantity": {"itemHash": EXO, "quantity": 1}}]}]},
  {"activityHash": LSM, "isVisible": True, "recommendedLight": 2010, "modifierHashes": [M_CHAMP]},
]
prof = {"profileInventory": {"data": {"items": []}},
        "characters": {"data": {"c1": {"characterId": "c1", "classType": 2, "light": 2010, "dateLastPlayed": "2026-11-25T00:00:00Z"},
                                "c2": {"characterId": "c2", "classType": 0, "light": 1990, "dateLastPlayed": "2026-11-20T00:00:00Z"}}},
        "characterActivities": {"data": {"c1": {"availableActivities": avail},
                                         "c2": {"availableActivities": [{"activityHash": LS, "isVisible": True}, {"activityHash": PVP, "isVisible": True}, {"activityHash": RAID, "isVisible": True}]}}},
        "characterInventories": {"data": {"c1": {"items": []}}}, "characterEquipment": {"data": {"c1": {"items": []}}}, "itemComponents": {"instances": {"data": {}}}}
ents = {"DestinyObjectiveDefinition/%d" % OBJ1: {"progressDescription": "Defeat champions"}, "DestinyObjectiveDefinition/%d" % OBJ2: {"progressDescription": "Complete the raid challenge"}}
ok = lambda r: {"ErrorCode": 1, "Response": r}

async def run(scn):
  global prof
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--disable-web-security']); pg = await b.new_page(viewport={'width': 1400, 'height': 1000})
    async def route(rt):
      u = rt.request.url
      if '/Destiny2/Manifest/' in u and u.rstrip('/').split('/')[-1].isdigit():
        k = '/'.join(u.rstrip('/').split('/')[-2:]); body = ok(ents.get(k, {}))
      elif 'Destiny2/Manifest' in u: body = ok({"version": "v7", "jsonWorldComponentContentPaths": {"en": paths}})
      elif '/c/lite.json' in u: body = lite
      elif '/c/' in u: body = tables[u.split('/c/')[1].split('.')[0]]
      elif '/Destiny2/Milestones/' in u: body = ok(pub)
      elif 'GetMembershipsForCurrentUser' in u: body = ok({"destinyMemberships": [{"membershipType": 3, "membershipId": "42"}], "primaryMembershipId": "42"})
      elif '/Profile/' in u: body = ok(prof)
      elif u.endswith(('.png', '.jpg')): return await rt.fulfill(body=b'')
      else: return await rt.continue_()
      await rt.fulfill(body=json.dumps(body), headers={"access-control-allow-origin": "*", "content-type": "application/json"})
    await pg.route('**/*', route)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    url = 'file:///home/claude/godroll-checker/today.html'
    await pg.goto(url)
    await pg.evaluate("() => { localStorage.clear(); localStorage.setItem('apiKey','k'); localStorage.setItem('clientId','1'); }")
    c1 = prof['characterActivities']['data']['c1']
    if scn == 'none':
      c1['availableActivities'] = [a for a in avail if a['activityHash'] not in (LSX, LSM)]
    elif scn == 'mot':   # only the c2 (not selected) character has today's, and only the activity type says lost sector
      c1['availableActivities'] = [a for a in avail if a['activityHash'] not in (LSX, LSM)]
      prof['characterActivities']['data']['c2']['availableActivities'].append({"activityHash": 120, "isVisible": True, "recommendedLight": 1980, "modifierHashes": [M_CHAMP]})
    if scn != 'signedout':
      await pg.evaluate("localStorage.setItem('auth', JSON.stringify({token:'T',exp:Date.now()+3600e3}))")
    await pg.goto(url); await pg.wait_for_selector('#lost .lsbox, #lost .lsproj', timeout=20000); await pg.wait_for_timeout(800)
    print('==', scn)
    print('summary tile:', [t.replace('\n', ' / ') for t in await pg.eval_on_selector_all('#topinfo .sum', 'e=>e.map(x=>x.innerText)') if 'Lost' in t])
    print('pills:', (await pg.inner_text('#tCat')).replace('\n', ' '))
    print('lost head:', await pg.inner_text('#lost .sect'))
    print('lost cards:', await pg.eval_on_selector_all('#lost .lsbox h3', 'e=>e.map(x=>x.textContent)'))
    if await pg.locator('.lsproj').count():
      print('proj:', (await pg.inner_text('.lsproj')).replace('\n', ' | ')[:700])
      print('week:', await pg.eval_on_selector_all('table.lsw tr', "e=>e.slice(1).map(x=>x.children[0].textContent+' '+x.children[1].textContent)"))
      await pg.click('#tCat [data-cat="lost"]'); await pg.wait_for_timeout(300); await pg.screenshot(path='/home/claude/tests/today_lost_pre_%s.png' % scn); await pg.click('#tCat [data-cat="all"]'); await pg.select_option('#lsPick', 'Perdition'); await pg.wait_for_timeout(300)
      print('after pick:', await pg.inner_text('.lsproj h3'), await pg.evaluate("localStorage.getItem('lsAnchor')"), '| tile', [t for t in await pg.eval_on_selector_all('#topinfo .sum b', 'e=>e.map(x=>x.textContent)')])
      await pg.click('#tCat [data-cat="lost"]'); await pg.wait_for_timeout(300)
      await pg.screenshot(path='/home/claude/tests/today_lost_%s.png' % scn)
    else:
      print('anchor saved:', await pg.evaluate("localStorage.getItem('lsAnchor')"))
    print('errors', errs); await b.close()
import copy
base = copy.deepcopy(prof)
async def main():
  global prof
  for scn in ['api', 'mot', 'none', 'signedout']:
    prof = copy.deepcopy(base); await run(scn)
asyncio.run(main())
