# D2 Roll Check: conventions for working on this repo

Personal Destiny 2 tool, run locally at `https://localhost:8443/` (`start-server-https.ps1`). It grades weapons against community wishlists, triages Armor 3.0 pieces, shows vendor stock and daily/weekly rotations, and tracks drops. No build step, no framework, no dependencies: plain HTML + vanilla JS + one shared stylesheet.

## Files

| File | Role |
|---|---|
| `index.html` | Weapons page **and** the Home view (`#home`), plus Settings, OAuth redirect handling, and Look up a weapon (`#lookup`) |
| `armor.html` | Armor triage (Armor 3.0 archetype/tier/tertiary rules, Gear to get, mods) |
| `vendors.html` | Vendors, Zavala & Shaxx panel, Xûr panel |
| `today.html` | Lost sector of the day, weekly milestones, featured activities, challenges |
| `vault.html` | Everything you own: vault, every character, equipped, postmaster. Search, filters, pull / vault / lock |
| `character.html` | One character like the in-game Character screen, every slot expanded. Equip, vault, move, lock, fill a slot from the vault |
| `tower.html` | Tower map: vendor pins that glow like in game, why (turn-ins, rank rewards, rewards waiting), what you can't get and why, each vendor's loot pool with rolls |
| `shaders.html` | Every collectible shader, owned vs missing (Collections), source, detail modal with vendor check |
| `rating.js` | Shared PvE vs PvP rating (`modeSplit`, `weaponModes`, `modeGraph`, `modeShort`, `modeDecide`), saved labels (`savedSplit`, `savedLabel`) and gear tier diamonds (`tierPips`, `tierIcon`). Loaded in `<head>` on every page, **before** the page script |
| `core.js` | Shared helpers every page used to copy: `bungie`, `bungieAction` (throttle retry), `net`, `idb` (one connection), `cacheGet/Set`, `ent`, `entMany`, `setStatus`, `toast`, `copyText`, `fillCharSel`, `setLock`, `transfer`, `pullFromPostmaster`, `pullTo`, `getAccount`, `autoRenew` (+ sign-in worker support), the Inventory section (`readInventory`, `inventoryHtml`) and the service worker registration. Loaded in `<head>` after rating.js. **Pages must not declare these names again** (a later declaration would replace the shared one) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Installable app: service worker (network first for pages, cache first for `?v=` files, never Bungie or config.js), app manifest, icons |
| `tests/` | Playwright page tests (`e2e_*.py`), `run_all.py`, trimmed god roll lists in `tests/fixtures`, speed benchmarks `perf_*.py` |
| `worker/` | Optional Cloudflare Worker for refresh tokens (`token-worker.js`, `wrangler.toml`, setup in `worker/README.md`) |
| `stream.js` | Shared Activity stream, tag-menu behavior, bottom-right notices. Loaded **after** each page's inline script |
| `theme.css` | Shared visual theme. Loaded **after** each page's inline `<style>` |
| `start-server-https.ps1` | Local HTTPS server (cert, netsh binding). `start-server.ps1` is the old http fallback |

Each page has its own inline `<script>` (page state, scan, render, page-only helpers like `loadDefs`, `updateAuthUi`, `handleOAuthRedirect`). The helpers every page needs live once in `core.js`; change them there, never copy them back into a page.

## Hard rules

- **Never rename or remove element IDs, `data-*` hooks (`data-act`, `data-copy`, `data-pick`, `data-tagset`, `data-note`, `data-open`, `data-view`), or event wiring.** Restyle with classes and `theme.css`; wrap elements in new containers if needed, but keep the element and its ID.
- **Don't change localStorage/IndexedDB keys** (users' tags, notes and caches live there). Current keys:
  - localStorage: `apiKey clientId auth bungieName tags notes myRolls wlPresets wlCustom wlUrl pullChar2 autoRefresh tagLockSync stream streamMute streamPinned streamSeen known:all weaponIndex weaponSummary armorIndex armorSummary armorRule:* acct:* vendShow vendMode vendHideCipher vendChar vendFold todayChar todayOpen todayCat lsToday lsAnchor authAuto pmMakeRoom vendSales shStatus shSource shSort vaultWhere vaultKind vaultSort charView enhPerks armorMeta armorSetSort armorSetFilter armorTopSets armorFold towerPos verdicts:weapons verdicts:armor charMode charAllShow charLabels` (sessionStorage: `relabelAt:w`, `relabelAt:a`, `acctMe`) (legacy `known:weapons`/`known:armor` are only read for migration)
  - IndexedDB cache: `wlSlim` (god roll rolls for owned weapons only, see Speed), `manifest2` (weapons), `manifestArmor` (armor/vendors/today items), `manifestToday` (activities), `manifestShaders` (shader list), `armorSetInfo` (set bonus text), `wl:<url>` (wishlists, 24 h), `ent:<Type>/<hash>` (single definitions), `towerMap` (your Tower map screenshot)
- **No secrets in files.** API key, OAuth client_id and token stay in the browser's localStorage. Never commit them; the repo is public.
- **Bungie OAuth:** Public client, redirect `https://localhost:8443/` (lands on `index.html`, which reads `sessionStorage.returnTo` to go back). No refresh token; sign-in lasts about an hour.
- **Bungie action limits:** item actions (lock, transfer, equip, socket changes) are throttled (~2 socket changes/sec). `bungieAction()` on every page retries a throttled call up to 3 times (350 / 700 / 1050 ms) when the message matches `thrott|too many|too quickly|try again`, so multi-step moves (`pullTo`) run back to back with no fixed sleeps. Bulk loops keep their own pauses. Perk/mod changes and equips only work in orbit, a social space, or offline.
- **DIM tags can't be written by outside apps.** Tags go to DIM only through the CSV export (`Id, Hash, Tag, Notes`), imported in DIM: Settings → Spreadsheets → Import tags/notes from CSV. One DIM tag per item; extra ticks go into the note.

## UI conventions (theme.css)

- Palette via CSS variables: `--bg #0D0F12`, `--panel #161A20`, `--panel2 #1C2129`, `--panel3 #222832`, borders `--line rgba(255,255,255,.08)` / `--line2 .14`, text `--text #F1F5F9`, secondary `--dim #94A3B8`, tertiary `--faint #64748B`.
- **Gold `--accent #E2B74B` only for primary actions, active states and key numbers** (one `button.primary` per view; everything else `button.ghost`). Verdict colors: god/exotic gold, keep `#3FB37F`, close/review `#5BA8E6`, trash `#E5534B`, legacy `#D98A3A`.
- Layout: `main` max-width `--wrap: 1440px`, side padding `padding-inline: var(--gutter)` (24px, 16px under 640px) on every page, 28px between sections, `overflow-x: clip` on `html/body` (**not** `hidden`, which breaks sticky elements).
- `font-variant-numeric: tabular-nums` is global so stats, timers and counts align.
- **Header** (identical on every page): brand `D2 Roll Check` → `index.html#home`; nav `Today · Weapons (index.html#weapons) · Armor triage · Vendors & Xûr`; active link gets a gold underline. Header is sticky (60px).
- **Weapons toolbar**: `.toolbar` is sticky under the header, two rows max (`.tb-scan`, `.tb-filter`).
- **Drawers**: rarely used controls go in `<details class="drawer">` (closed by default) with a one-line `.dim-lbl` hint, e.g. "DIM Export & Bulk Actions", "Trash rules", "DIM sync".
- **Cards** (`.card.wcard`, armor adds `.acard`): flex column, equal height. Order is always
  1. `.chead`: icon, `.ctitle` (name + one-line meta), `.cstats` (score / Aegis / tier / verdict badge)
  2. `.body`: reason, key chips (recommended perks or armor stats); everything else behind `details.more` ("Show all perks & notes")
  3. `.cfoot`: one `details.tagpop` (🏷 tag menu wrapping the existing `tagBoxes()` + Apply) and `.cacts` small buttons (lock icon, Pull, Apply perks, Copy DIM, note)
  Card click opens details; the click handler must ignore `button, select, label, input, a, textarea, details, summary`.
- **Notices**: `#status` and `.toast` live in `#noticeStack` (fixed bottom-right, z-index 1000), moved there by `stream.js`. Info fades after 6 s, errors (`setStatus(msg, true)`) stay until dismissed. Never put status text back in the page flow.

## Weapon detail view (index.html: `loadDetail` / `renderDetail`)

- Sockets are classified from the manifest, not by position: `DestinySocketTypeDefinition.plugWhitelist[].categoryIdentifier` finds the **mod** socket (`v400.weapon.mod_*`) and the **masterwork** socket (`*masterworks.stat*`); each plug's `plug.plugCategoryIdentifier` / `itemTypeDisplayName` filters the perk columns (`isPerkPlug`). The "weapon perks" category (4241085061) can contain empty, enhancement and masterwork sockets; those never become perk columns.
- Perk columns get headers from the plug type: Barrel / Magazine (or the weapon's own type, e.g. Bowstring, Blade), Perk 1, Perk 2, Origin. Enhanced and normal versions of a perk collapse to one icon; the Enhanced toggle (`D.enh`, localStorage `enhPerks`) shows the enhanced one where it exists.
- **State:** `D.base` = the copy's current plugs (or defaults), `D.preview` = perk picks, `D.extra` = mod/masterwork picks. Stats use `base + preview + extra`. **Apply selected perks** and **Save as My god roll** only look at `D.preview` / perk columns, never `D.extra`: mods and masterworks are stat previews only (the free socket call can't insert them).
- Masterwork list = the strongest plug per stat (+10) plus "No Masterwork" (`D.extra[mwIdx] = 0`). Mods grid = one plug per name, empty/default plugs dropped; clicking the selected mod again removes it.
- **Recommended rolls buttons** (right panel, above Masterwork): `❖ PvE god roll`, `❖ PvP god roll`, `★ My god roll`. `rollsFor(mode)` takes list entries tagged `pve`/`pvp` (`both` counts for each; untagged entries are only used when a weapon has no tagged ones, ~0.6% of Community entries), groups them by trait pair, and picks the most-recommended barrel/magazine plus any listed mod/masterwork. Sorted by number of backing lists, then god-tagged, then frequency. Clicking again cycles (`D.roll` = mode, idx, label shown as "Previewing: PvE roll 1 of 2 · Community / Aegis"). A mode with no rolls shows a disabled "No PvP roll listed". `previewRoll()` writes perks into `D.preview` (prefers the plug this copy owns so Apply works) and mod/masterwork into `D.extra`. Manual perk clicks, Reset and a successful Apply clear `D.roll`.
- Masterwork list only shows stats in the weapon's stat group (`scaledStats`), so a hand cannon never offers Blast Radius, Velocity, Charge/Draw Time or Shield Duration.
- Verdict badges carry the mode (`it.r.mlabel`): the dropdown's mode when it's PvE only / PvP only, otherwise the tags of the matched rolls (`modeLabelOf`). Shown as `GOD ROLL · PvE`, `CLOSE · PvP` on cards and in the detail header. Changing the dropdown re-rates cards and refreshes an open detail view.
- Header subtitle: item type · intrinsic frame · damage type (`defaultDamageTypeHash`) · ammo (`equippingBlock.ammoType` 1/2/3 = Primary/Special/Heavy); status badge = copy location/power/tier or "Not in inventory".

## Armor community meta (armor.html: `META_ARCH`, `META_SETS`)

Community opinion, not Bungie data. Derived Nov 2026 (after Monument of Triumph 9.7.0) from published stat priorities and verdicts. Keep these tables in sync with this section; update both when the meta moves.

- PvE basis: Powerhouse is the consensus best endgame DPS archetype (Weapons + Super); Weapons is the most useful PvE stat; Class + Weapon for high-tier raids, Class + Melee for high-tier solo, Super + Grenade for regular raids; Health is mostly ignored in PvE.
- PvP basis: Weapons 150+, then Super 70-100, then Health 120-150, then Class / Grenade / Melee by playstyle.
- Tier labels: `S · Top Pick`, `A · Strong`, `B · Niche`, `C · Skip`. Each badge has a hover reason.

| Archetype | Stats | PvE | PvP |
|---|---|---|---|
| Powerhouse | Weapons / Super | S | S |
| Gunner | Weapons / Grenade | S | S |
| Specialist | Class / Weapons | A | A |
| Grenadier | Grenade / Super | A | B |
| Reaver | Class / Melee | A | C |
| Demolitionist | Grenade / Class | B | C |
| Paragon | Super / Melee | B | B |
| Skirmisher | Melee / Weapons | B | A |
| Brawler | Melee / Health | B | B |
| Colossus | Super / Health | C | A |
| Bulwark | Health / Class | C | B |
| Siegebreaker | Health / Grenade | C | B |

Set tiers use their own labels (`SET_TIER`): `S · Top Set`, `A · Strong`, `B · Niche`, `C · Filler`. A set only gets a tier when a published guide gave a verdict; otherwise it shows `Not rated` (dashed badge). Do not invent tiers. Sources (Nov 2026): Nerd's Chalk dungeon set ranking (Jun 2026: Top-tier = S, Very good = A, Good/Niche = B, Skip/Broken = C), gamingpromax set bonuses (verified Nov 13 2026), gamer.org (Jul 2026), bo3.gg; drop sources from blueberries.gg.

| Set | Source | PvE | PvP |
|---|---|---|---|
| Techeun's Regalia | Shattered Throne | S | |
| Exodus Down | Nessus | S | |
| Iron Battalion | Iron Banner | S | B |
| Apostate's Blade | Pit of Heresy | S | |
| Dark Age | Warlord's Ruin | S | |
| Taken King | Ghosts of the Deep | S | |
| CODA | Prophecy, Trials | A | |
| Promised | Salvation's Edge | A | |
| Atheon's Memory | Vault of Glass | A | |
| Dreambane | Moon | A | |
| Great Hunt | Last Wish | A | |
| Flain | Sundered Doctrine | A | |
| Yearning Echo | Grasp of Avarice | B | |
| Sage Protector | Equilibrium | B | |
| Nezarec's Nightmare | Root of Nightmares | B | |
| Spacewalk | Vesper's Host | B | |
| Tex Mechanica Custom | Spire of the Watcher | B | B |
| Last Discipline | Crucible Ops | B | B |
| SRL / Circuit | SRL | B | B |
| Deep Explorer | Duality | C | |
| Descending Echo | | C | |
| Cruel Electrum | Trials | | S |
| Triumphal Anthem | Crucible Ops | | A |
| Per Audacia | Competitive Crucible | | A |
| Twofold Crown | Trials | | A |
| New Demotic | Trials | | A |

Every other known set (Pantheos Resplendent, Bushido, Techsec, Ferropotent, Luminopotent, Iron Panoply, Wild Anthem, Shrewd/Thriving Survivor, AION sets, destination sets, older raid sets) is listed in `META_SETS` with its source only.

- Every section folds from its header (`.foldhead` inside a `[data-fold]` box, class `folded`): `classes` (summary), `get` (Gear to get panel), `arch` (archetype table), `sets`, `top`, `oldex`, `list` (toolbar + cards). Folded keys in localStorage `armorFold`; `applyFolds()` runs after each Gear to get render. Each header has a › chevron on the left and a `Collapse` / `Expand` button (`.ftog`, text from CSS) on the right; the top bar has `Collapse all` / `Expand all` (`[data-foldall]`). Clicks on other chips, buttons and inputs in a header don't fold.
- Gear to get: columns `PvE` and `PvP` sit between `Stats` and the slot columns. Filter chips `All archetypes` / `Top PvE picks` / `Top PvP picks` (localStorage `armorMeta`). Top picks = every S and A archetype for that mode (owned or not), in `META_ARCH` order; slots without a Tier 5 get the `want` highlight and a count line.
- Bottom of Gear to get: "Slots with no Tier 5 yet" renders only when at least one slot lacks a Tier 5, as a slim strip (`#noT5`) above the cards. Then a 3-card grid (`.getcols`: `1.1fr 1.1fr .8fr` at 1200px+, 2 columns at 900px+, gap 20px, card padding 20px, cards align to the top): Set progress · Top Community Sets · Old exotics.
- Set progress: every owned set for the class (no cap), 2 lines per set. Line 1: name, `x/5` (colored), `4pc ready` / `2pc ready`, pills `PvE S` / `PvP A` (`–` dashed when not rated). Line 2 (muted): `Missing:` slots · below-T4 slots · source. 2pc/4pc bonus text is the hover tooltip on the set name (`bonusTip`). Sort chips `Community rank` / `Pieces owned` (`[data-ssort]`, localStorage `armorSetSort`). Filter box `#setFilter` (not saved) plus chips `All` / `Incomplete` (<5) / `4pc Ready` (`[data-sfil]`, localStorage `armorSetFilter`); filtering toggles `.hidden` on rendered rows so typing keeps focus.
- Bonus text: `loadSetInfo()` reads `DestinyEquipableItemSetDefinition.setPerks` (`requiredSetCount`, `sandboxPerkHash`) and resolves names/descriptions with `entMany('DestinySandboxPerkDefinition', ...)`. Cached in IndexedDB `armorSetInfo` `{version, info: {setName: [{c, n, d}]}}`, separate from `manifestArmor`. Runs after the first render, then re-renders Gear to get.
- Top Community Sets (`#topSets`): every S and A set in `META_SETS`, ranked, chips `Both` / `PvE` / `PvP` (`[data-topm]`, localStorage `armorTopSets`). Each row is a bordered mini card (padding 12px 14px): rank, name (bonus tooltip), pills / one-line takeaway (`why`) / source and "You own x/5" for this class.
- Old exotics: grouped by name and slot with a `×N` badge (`.dupn`), listed under slot subheaders (`.oxhead`) in `SLOT_ORDER`, no bullets. "Slots still on old armor only" uses the same subheader style.

## Data sources

- Bungie.net API: profile components `102,200,201,204,205,300,304,305,310,800,1200` (800 = Collectibles, Shaders page); `GetVendors` (`400,401,402,300,304,305,310`, needs the vendor OAuth scope); public `/Destiny2/Milestones/`; manifest JSON tables.
- Lost sector of the day is **not** in public data: it's the lost sector a character can run at Expert/Master in `characterActivities.availableActivities` (component 204). `isLostSector()` matches "Lost Sector" in the activity name, original name, description, mode name, or activity type name (`T.act[h].at` = `activityTypeHash`, `T.atype` from `DestinyActivityTypeDefinition`). `lostFromAccount()` merges all characters (selected first), so one character having it is enough. Results are cached per daily reset in `lsToday` (non-empty only).
- Rotation fallback: when no character lists it and there is no cache, `lsProjectionHtml()` projects today's lost sector from `LS_CYCLE` (11-day order, champions, shields), anchored by `LS_DEFAULT_ANCHOR` (2025-07-06 reset = Veles Labyrinth, from published 2025 schedules). It is an estimate for Monument of Triumph, so it self-corrects: every time Bungie shows a lost sector that is in the cycle, `setLsAnchor(name, 'api')` stores localStorage `lsAnchor` `{day, name, src}`; the user can also pick today's from a select (`src: 'manual'`). Reset is 17:00 UTC (`RESET_H`). Shows today's card plus a 7-day table. Champion/shield values are the last published ones; unknown ones show "Not published". If the rotation changes, update `LS_CYCLE`.
- `manifestToday` cache has a `schema` number (`T.schema`); bump it when the cached table shape changes so users re-download.
- The Lost Sector pill always counts the daily lost sector: from any character, from the cache, or the projected one.
- Today category pills (`state.cat`, localStorage `todayCat`): All, Lost Sector, Strikes / Nightfall, Raids, Dungeons, Crucible, Weekly / Portal. `catsOf()` classifies by activity name/type/mode; "Weekly / Portal" = weekly milestones, Portal-featured, or has weekly challenges. Counts are live and respect the search box; a filter hides empty sections and scrolls to the first match.
- Xûr: schedule-based (Fri 17:00 UTC → Tue 17:00 UTC). His Strange Coin shop is in vendor data all week, so presence in the data doesn't mean he's arrived.
- Wishlists (DIM format) from `PRESETS` in `index.html`: Community (voltron), Aegis Endgame PvE, Monument PvE/PvP, optional trash list. Footer roll counts = lines starting with `dimwishlist:`.

## Vault (vault.html)

- Nav order on every page: Today, Weapons, Armor triage, Vault, Character, Vendors & Xûr, Tower, Shaders. Home Jump to has Vault and Character cards.
- Profile `components=102,103,200,201,204,205,300`; names/icons from the shared `manifestArmor` cache (`loadDefs`). `readItems()` turns vault + character inventories + equipment into rows `{id, hash, name, icon, type, it, kind, rar, cls, qty, charId, equipped, postmaster, locked, loc, where, power, gearTier, set}`. Subclasses (itemType 16) are skipped. `where` is `vault`, a character id, or `pm`.
- Space strip (`#vSpace`, `readSpace()` / `spaceHtml()`): profile components now include `103` (currencies). Slots used = number of stacks per `profileInventory` bucket (General 138197802, Consumables 1469714392, Modifications 3313201758), against `itemCount` from `DestinyInventoryBucketDefinition` via `entMany` (cached), so capacity changes need no code change. Bars go gold at 85% and red at 95%. Currencies with a quantity above 0 are listed with their icons.
- Groups (`KINDS` by DestinyItemType): Weapons, Armor, Mods & shaders, Consumables & materials, Ghosts & cosmetics, Quests & bounties, Other.
- Filters: chips Where (`vaultWhere`) and What (`vaultKind`), sort (`vaultSort`), search box (not saved). Search is every word must match across name, type, location, rarity, class, `t5`/`tier 5`, set, `locked`, `equipped`, `postmaster`. `/` focuses the search box. 200 rows per page with Show more.
- Actions only on instanced items when signed in: Pull (to the header Pull-to character, uses `pullTo`, handles postmaster), Vault (`transfer`), Lock for weapons/armor (`setLock`).

## Character (character.html)

- Profile `components=100,102,103,200,201,205,300`. Tabs per character (localStorage `charView`), emblem banner, Bungie name, race and class, power, stats (names and icons from `DestinyStatDefinition` via `entMany`, Power stat left out), currencies.
- Slots like the in-game screen: left Subclass, Kinetic, Energy, Power, Ghost; right Helmet, Arms, Chest, Legs, Class item; then Emblem, Sparrow, Ship. Each slot shows the equipped item (large) and every inventory item for that bucket (the in-game side boxes, expanded), plus dashed empty boxes up to 10 per bucket.
- Click an item: Equip (`EquipItem`), Vault, To <other character> (`pullTo`), Lock. Click an empty box: picker of vault items for that bucket and class (instanced only), with a filter box; picking calls `transfer(..., false, charId)`.
- `sync()` moves items whose `charId` was cleared (by Make room through `byId`) out of the character view into `state.vault`.
- Postmaster row above the slots: the character's Lost Items as 21 boxes with `(n/21)` and a Pull all button (opens the 📬 panel). Click an item for its roll and a Pull button (`pullFromPostmaster`, with Make room).

## Roll inspector (stream.js, every page)

- Any element with `data-roll="<itemInstanceId>" data-rh="<itemHash>"` shows the item's roll: hover after 300 ms on mouse devices, tap or click everywhere (clicks on buttons inside are ignored). Used by the Postmaster panel rows and Vault tiles; the Character page item card calls `window.rollHtmlFor(id, hash)`.
- Reads one item: `GET /Destiny2/{type}/Profile/{id}/Item/{instanceId}/?components=300,304,305,310`. Plugs and stats are named with `entMany`; shaders, ornaments, trackers, mementos and empty sockets are skipped (`SKIP_PLUG`). Cached per item for the life of the page; a perk change clears that item's cache.
- Layout like DIM's item popup: stats (bars to 100, numbers only for RPM, magazine, draw and charge time and similar, `NOBAR`), the intrinsic frame, then one row per perk socket that has more than one option in component 310 (`reusablePlugs`): the active perk on the left, the other options as round buttons on the right (enhanced ones gold, `canInsert: false` ones dimmed), then single-plug sockets (masterwork, mods, origin traits) as small icons.
- Clicking an option (`[data-swap]`, delegated in capture phase) calls `InsertSocketPlugFree` with `socketIndex`, `plugItemHash`, the item id and the item's character (`characterId` from the item response, else the Pull-to character, else the first character), then re-reads the item and redraws the card in place (`[data-rollbox]`). Failures explain that perk changes only work in orbit, a social space or offline.
- Mods: single-plug sockets whose item definition has a `reusablePlugSetHash` (and aren't masterwork, intrinsic, origin, catalyst or tracker) are editable, empty ones included. Clicking one (`[data-modpick]`) lists the account's unlocked plugs for that plug set from `profilePlugSets` plus `characterPlugSets` (profile `components=305`, fetched once per page, refreshed after 10 minutes), with a filter box and energy cost. Picking one (`[data-modset]`) calls `InsertSocketPlugFree` and redraws the card.
- Hover mode keeps the card open for 300 ms after the pointer leaves the item, so you can move into it and click a perk.
## Moving to a character (every page)

- `transfer(i, false, charId)` on every page frees a slot first when the destination bucket is full, using the same Make room logic as the postmaster (`pmEnsureRoom` before, retry once after a no-room error). `transfer(i, true, charId)` tells stream.js the slot is free (`pmLeft`). Covers vault pulls on Weapons, Armor, Vault, Character and the Activity stream.

## Postmaster (stream.js, every page)

- `trackDrops(p)` also calls `pmCapture(p)`: Lost Items (bucket 215593132) per character from `characterInventories`. Header button `#btnPM` (📬 + count, red when a character has 18+ of 21) opens `#pmPanel` (styled like the Activity panel).
- Pull one stack or Pull all per character: `PullFromPostmaster` with `stackSize = quantity` and `itemId` = instance id or `'0'` for stacks. Failures are listed in the status box.
- Make room (checkbox in the panel, localStorage `pmMakeRoom`, on by default): on a no-room error (`DestinyNoRoomInDestination` / "no item slots"), `destBucket()` finds the item's bucket (`state.defs[h].b` or the full definition), `makeRoom()` moves the lowest rarity, then lowest power, **unlocked** item in that bucket on that character to the vault (`TransferItem`, whole stack), then retries the pull once. For instanced items it also checks first (`bucketFull()`: items in that bucket on the character, plus the equipped one for equippable buckets, against `DestinyInventoryBucketDefinition.itemCount`) and makes room before pulling. Stacks rely on the no-room answer because they can merge into an existing stack. Never moves locked or equipped items. Every page's `pullFromPostmaster()` (the 📬 Pull button on item cards) uses the same logic through `window.pmEnsureRoom`, `pmIsNoRoom` and `pmLanded`. Buckets that can't go to the vault (`NO_VAULT`: engrams, pursuits, subclass, clan banners) report instead. `pmCapture()` keeps each character's inventory (`inv`) for this. Item names come from `state.defs`, else `ent('DestinyInventoryItemDefinition', hash)`.
- Postmaster to vault: Bungie has no direct move, so `pmPull(cid, pick, btn, true)` pulls to the character (with Make room) and then `TransferItem` to the vault. Buttons: per item Vault (`data-pmv`) and All to vault (`data-pmallv`) in the panel; Send to vault on the Character page postmaster card (`window.pmToVault`). `NO_VAULT` buckets (engrams, pursuits) are refused with a note to use Pull.
- Postmaster warnings like DIM: `pmLevel(n)` is `almost` from 15 and `full` at 21; `pmLabel(n)` gives `ALMOST FULL! (19/21)` / `FULL! (21/21)`. The 📬 button turns amber (almost) or red and pulsing (full), its tooltip lists every character, the panel and the Character page postmaster box get the same colors, and `pmWarn()` shows a status message once per session per character each time one crosses into almost full or full (delayed 1.2 s so the page's own scan message doesn't overwrite it; sessionStorage `pmWarn_<charId>`).
- Keep / trash labels on the Character page: the Weapons page saves `verdicts:weapons` ({at, m: {instanceId: [verdict, reason, 'rank/count', oldFlag]}}) and Armor triage saves `verdicts:armor` ({at, m: {instanceId: [v, why, legacy, exotic]}}) after each scan. character.html `verdictOf(i)` maps them to tile tags: GOD, CLOSE, TRASH, EXO, OLD (old gear, get newer; purple for old exotics), KEEP, REVIEW. Items picked up after the last scan show no tag until that page scans again. Toggle stored in `charLabels`. When a map is missing or older than 6 h (or "Refresh labels" is clicked), `autoLabel()` loads index.html#weapons / armor.html in a hidden 1px iframe; those pages scan on load and save the map, the parent's `storage` listener redraws and removes the frame (150 s timeout). Skipped when the token has under 5 min left so a frame never starts a sign-in renewal.
- Character page "All + vault" view (`charMode` = 'all'): DIM style columns per character plus the vault, rows per bucket. HTML5 drag and drop: drop on a character cell moves it there (vault → transfer with make room, other character → pullTo), on the vault cell sends it to the vault, on an equipped tile moves then equips. Drops only land in the matching bucket. Equipped items are not draggable. `render()` is deferred while a drag is in progress. Search box dims tiles that don't match (name, type, tier, label, "locked"). Mouse only; on touch use the click popover. Character filter `charAllShow` ('all' or a character id) shows one character column plus the vault; the first character (last played) is marked active.
- One character view drag and drop (`wireDragOne`): tiles of the shown character drag onto another character's tab (pullTo via the vault) or the 🏦 Vault tab (transfer to vault). Clicking the Vault tab switches to All + vault.
- Pinned Activity panel (`body.streampinned`, 390px wide): under 1710px the header wraps and the nav tabs drop to their own row so no control sits behind the panel. `placeRoll` (stream.js) and `place()` (character.html) open popovers to the left of the panel. The postmaster panel sits above it (z-index 51).
- Dismantle guard: an item missing from the profile is only reported as dismantled after it is missing on two refreshes at least 45 s apart (`known:miss` in localStorage). Stops false "Dismantled" entries right after a transfer or pull.
- Activity stream Pull/Lock: only the Weapons page (weapons) and Armor page (armor) handle their own items through `runAction`. On every other page the stream acts on the profile record (`actOther` → `pullTo`, with Make room), updates the page's own record through `byId`, calls `render()`, and re-reads after 2.5 s.
- Pages must provide `auth`, `bungieAction`, `scan`, and may provide `render`. The `#authStatus` text is hidden by theme.css to keep the header on one line; stream.js copies it into the Sign out button tooltip.

## Shaders (shaders.html)

- Nav: every page's header has `Shaders` after `Vendors & Xûr`; Home has a Shaders card in Jump to. Same header, stream panel, auth banner and `stream.js` hooks as Today (`PAGE = 'shaders'`). OAuth `returnTo` = `shaders.html`.
- `loadManifest()` downloads `DestinyInventoryItemLiteDefinition` once and fills both `manifestArmor` (shared item names for the Activity stream) and `manifestShaders` (`{version, v: 1, list}`) when either is missing. Bump `v` if the row shape changes.
- A shader = lite item with `itemCategoryHashes` containing 41, or `itemType 19` + `itemSubType 20`, with a `collectibleHash` that exists and isn't redacted in `DestinyCollectibleDefinition`. One row per collectible, then one per name (newest `index` wins). Row: `{h, ch, n, i, wm (iconWatermark), src (sourceString), x (index), fl, tier}`. Default/dummy shaders have no collectible, so they drop out.
- Owned: profile `components=...,800`. `readOwned()` treats a collectible as owned when `(state & 1) === 0` in `profileCollectibles` or any `characterCollectibles`. No collectible data (privacy) = status unknown with a message.
- Signed out: full list, search, source and sort work; status chips are dimmed and badges say "Sign in to check".
- Filters: search (name or source), status chips `All / Owned / Need to get` (`shStatus`), source select (`shSource`, `SOURCES` regex buckets on `sourceString`, plus Other), sort (`shSort`: Newest = manifest `index` desc, an approximation; Name; Owned first; Missing first). Grid renders 120 cards at a time with Show more.
- Detail modal: big swatch with watermark, source text, category, season (`seasonHash` from the full item definition via `ent()`, then `DestinySeasonDefinition`), vendor check, Copy name. Esc or backdrop closes.
- Vendor check: `vendors.html` writes localStorage `vendSales` `{at, vendors: [{n, due, h: [itemHash]}]}` after every vendor load. Shaders ignores vendors whose `due` has passed. No data = prompt to open the Vendors page.

## Vendors (vendors.html)

- Bulk `GetVendors` returns no sockets for sale items. When a vendor's gear comes back without sockets, the page asks that vendor alone (`/Vendors/{hash}/?components=300,304,305,310,402`, Zavala/Shaxx first, then Xûr, up to 40 vendors, 4 at a time) and merges `itemComponents` and `sales` back in.
- Weekly reward tracks ("Weekly: Vanguard Arms Rewards", visible or hidden) fold into Zavala's or Shaxx's box (`weeklyOf`), gear with a visible roll only, pill `Weekly reward`, decision `Go get it` instead of `Purchase`.
- Weapon badges follow the PvE / PvP bars (`rate()`, after the wishlist verdict): better mode 70+ makes Maybe / Unrated into Buy (Have it when you own a god roll), 45-69 makes Unrated into Maybe, under 45 makes Maybe / Unrated into Skip. Rolls for = PvE only / PvP only uses just that mode. Trash list items stay Skip.
- Every rated card has a decision line (`decisionLine`): Purchase / Go get it, Maybe, Your call, Ignore, with a one-line reason.
- Jump bar `#vNav` (sticky under the header): Xûr, Zavala & Shaxx, one link per vendor with its item count, Rolls when bought, plus Expand all / Collapse all. Vendor sections are `details.vgroup` (`id="vg-<hash>"`, `data-vh`) with a divider; folded hashes are saved in localStorage `vendFold`. Jumping opens a folded section.
- Xûr (when he is here) is `details.xurbox` `#vg-xur` (fold key `xur`) with a one-line gist (to purchase / maybe) in the summary. Zavala and Shaxx boxes are `details.corebox` (`id="vg-<hash>"`, same `vendFold` key); the verdict line stays visible when folded. Each gets its own jump link.
- Roll popup on vendor cards: icon and name carry `data-roll="v:<vendorHash>:<index>:<itemHash>"`. stream.js `readRoll` gets the sockets, reusable plugs, stats and PvE/PvP split from `window.vendorRoll(id)` (no request). Perk and mod buttons are disabled for vendor rolls. Category names have Bungie's `{var:...}` placeholders stripped.
- Items that roll when bought (`#vSkipped`) show as icon tiles grouped by vendor (`skippedGrid`), linked to light.gg, name and type in the tooltip.
- Drawer `#vDiag` "What Bungie sent" lists every vendor (hidden ones too) with item, gear and rolled counts; ★ marks rows that look like a weekly track.

## Tower (tower.html)

- Same shell as Shaders (`PAGE = 'tower'`, `returnTo` = `tower.html`). Profile `components=102,103,200,201,205,300` (what you hold: profile inventory, the selected character's inventory, profile currencies → `state.have`), then `GetVendors` `400,401,402` for the Pull-to character. Vendors whose destination or place matches `tower|last city`.
- **Pins** = visible vendors with their own `displayProperties.mapIcon` (what the game draws on the map), plus Xûr (`XUR_HASH`). Every other Tower vendor (hidden or not: "Weekly: Vanguard Arms Rewards", "Armor", engram and focusing screens) is a sub screen folded into a pin by `parentOf()`: the pin's short name inside the sub screen's name, else `PARENT` keywords over its name, categories and cost item names (Vanguard → Zavala, Iron → Saladin else Shaxx, Crucible → Shaxx, Strange / Exotic Cipher → Xûr...). Its items join the pin's loot pool under the sub screen's name and its reasons get "(sub screen)". Unmatched ones are only listed in the diag drawer.
- Glow reasons (`analyze()`), all from Bungie data: vendor progression `rewardItemStates` Earned (2) and not Claimed (4) → rank-up reward; sale items paid only with engrams / tokens / ciphers / keys (`TURNIN`) you can afford → "You have N X to spend here"; augment RewardAvailable (2) → reward waiting; augment New (8) → "N new items in stock" (the game's NEW tag). A turn-in or reward whose `saleStatus` isn't 0 is blocked (⚠): vendor `failureStrings[failureIndexes]`, else `ST` flag text. A pin whose only reasons are blocked glows red.
- Map: `MAP_SVG`, a blueprint drawing traced from the in-game map screen (2576 x 1406, `MAP_W`/`MAP_H`; Bazaar, Courtyard, Hangar, lower deck, the plaza and hex). Pin spots `TOWER_POS` (name regex → percent, measured on that screen by matching each vendor's map icon; a 4th value 1 = off the left edge, drawn with ‹). Glow = rotating ray ring (`.ray`, conic gradient) like the game. Labels show on hover.
- Map options drawer (`#twOpts`): Move pins (`#twArrange`, saved in localStorage `towerPos` `{v: 2, pos: {vendor name: [x%, y%]}}`, older shapes are ignored), Reset pins, Use my map screenshot (`#twShot`, data URL in IndexedDB `towerMap`, this browser only; the drawing and pin icons hide so the glow rings sit on the game's icons), Remove screenshot.
- Below the map `#twList` lists only glowing vendors with their reasons. Drawer `#twDiag` "What Bungie sent": per pin item count, sub screens folded in, item augment flags, rank reward states, glow.
- Hover a pin (220 ms) or click it / a list row: `#twPanel` loot pool grouped by category (sub screens by name), Can get / Can't get / Reward, reasons, costs vs what you hold. Gear rolls: each vendor or sub screen that sells gear is read alone once (`single[vh]`, up to 6 per panel), then names carry `data-roll="v:<vh>:<index>:<hash>"` for the shared roll popup. Closes with ✕, Esc or a click outside. Xûr dims outside Fri 17:00 to Tue 17:00 UTC.
- IndexedDB adds `towerMap`.

## Hosting

- GitHub Pages, deployed by `.github/workflows/pages.yml` on every push to `main` (Pages `build_type=workflow`): https://vleejr-lgtm.github.io/d2-roll-check/ . The workflow copies `*.html *.css *.js manifest.webmanifest .nojekyll` and `icons/` into `_site` (no .md, .ps1, tests or worker; a local `config.js` is removed), stamps `__BUILD__`, and retries `deploy-pages` once after 20 s when GitHub can't see the fresh artifact yet and writes `_site/config.js` from repo secrets `BUNGIE_API_KEY` and `BUNGIE_CLIENT_ID` (format-checked, fails the deploy if missing).
- `config.js` sets `window.D2RC_CONFIG = { apiKey, clientId }`. Every page loads it in `<head>` (`onerror` removes the tag, so a missing file on localhost is harmless). `SHARED_APP` is true when both values are present; then `ls.get('apiKey' | 'clientId')` returns the config values and ignores localStorage, Settings hides `#keyFields` / `#keyHelp` and shows `#sharedApp`, and Save doesn't write the key fields.
- `config.js` is in `.gitignore`. Never commit it, and never put keys in any other file. Locally (no config.js) Settings works as before with your own localhost Bungie app.
- Each address needs its own Bungie app (one Origin + one Redirect URL per app). localStorage is per origin, so tags and notes don't carry between localhost and the hosted site.

## Sign-in renewal

- Public Bungie clients get ~1 hour access tokens and no refresh token. Each page has `autoRenew()` (just above `const PAGE`): if the user has signed in before (localStorage `authAuto = '1'`, set in `handleOAuthRedirect`, cleared by Sign out), it sends them through bungie.net/en/OAuth/Authorize again, which returns straight away for an app already approved.
- Triggers: page load, every 30 s, and when the tab becomes visible. Renews when the token has expired, or has under 4 minutes left and there was no input for 60 s. Skips while `state.scanning`, in hidden tabs, on http, and while a `?code=` is being finished.
- Loop guard: sessionStorage `renewAt`, at most one renewal per tab every 3 minutes. `returnTo` is the current page plus a simple `#hash`; `handleOAuthRedirect` accepts `^[a-z]+\.html(#[a-z]+)?$`.
- Optional sign-in worker (`worker/`): with repo secret `BUNGIE_TOKEN_PROXY` set, config.js gets `tokenProxy`; `exchangeCode()` (core.js, used by `handleOAuthRedirect`) sends the sign-in code to `<proxy>/token`, and `autoRenew()` calls `refreshQuietly()` (`<proxy>/refresh`) 5 minutes before expiry, no page change. `auth` then also holds `refresh` and `rexp` (90 days). A failed refresh clears `refresh` and the redirect renewal takes over. The Bungie app must be Confidential; the worker holds the client secret (Cloudflare secrets), answers only `ALLOWED_ORIGIN`, stores nothing. Never put a client secret in config.js or the repo.

## Testing

- Tests live in `tests/` and run on every pull request (`.github/workflows/tests.yml`, Playwright 1.63, Chromium). Locally: `python tests/run_all.py -j 4 [name filter]`. A test passes when its last `errors [...]` line is `errors []` with no Traceback; failures are retried once alone (busy machines time out); only a double failure fails the run. Screenshots go to `tests/out/` (uploaded by CI when a run fails).
- The scripts use fixed paths (`/home/claude/godroll-checker`, `/home/claude/probe`, `/home/claude/wl`, `/home/claude/tests`); `run_all.py` symlinks them to the repo, `tests/fixtures` and `tests/out` on a fresh machine. `tests/fixtures` holds the god roll lists trimmed to the weapons the tests use.
- New features need a test (or a check added to an existing one) in `tests/`.
- Playwright scripts with mocked Bungie responses (`page.route('**/*')`, Chromium with `--disable-web-security`, pages opened from `file://`).
- Mocks serve empty bodies for wishlists other than voltron, so the footer shows **0 rolls** for Aegis/Monument in tests. That's expected; real lists parse (Aegis ≈198k rolls, Monument PvE 25, PvP 5).
- Controls inside closed drawers/tag menus aren't clickable in tests: open them first (a MutationObserver init script that sets `details.drawer` / `details.tagpop` open) or click via `element.click()`.
- Before shipping: run every page test, diff the list of element IDs against the previous build, and check screenshots with drawers closed.

## Git workflow

- `main` is protected (ruleset `protect-main`: PR required, no force push, no deletion). Work on a branch, then:
  `git checkout -b <name>` → `git add .` → `git commit -m "..."` → `git push -u origin <name>` → `gh pr create --fill` → `gh pr merge --squash --delete-branch` → `git checkout main` → `git pull`.
- Review outside PRs carefully, especially anything touching `bungie()`/`bungieAction()` or sending data to a host other than bungie.net.
- Human-facing text in the app and README: plain, direct, no dashes as punctuation, no AI filler words.

## PvE vs PvP rating (rating.js, every page)

- `modeSplit(hash, have, nameOf, typeOf, wl)` scores one roll for PvE and PvP separately from the merged wishlists. Per mode: `best` = share of the closest recommended roll this copy can have (selected or selectable perks), `combo` = share of a recommended trait pair, `full` = rolls fully matched. Overall = 50% best + 35% combo + 15% min(full/3,1), plus the Aegis tier nudge for PvE (S +8, A +5, B +2, C 0, D -4, E -7, F -10), clamped 0..100. A roll on a trash list for that mode = 0 with the trash flag. No rolls for a mode = null. Untagged rolls count for both modes only when the weapon has no tagged ones (same rule as `rollsFor`).
- Compact form `{ pve: [overall, combo%, best%, full, trash] | null, pvp: [...] | null, aegis }`. The Weapons page saves it as the 5th element of each `verdicts:weapons` entry, so every page can show it by instance id (`savedSplit(id)`, parsed once per 3 s).
- Grades: S 88+, A 75+, B 60+, C 45+, D 30+, F below. Per mode call: Keep 70+, Maybe 45+, else Trash. `modeDecide()` takes the better mode: "Keep for PvE/PvP/both", "Maybe, best in X", "Trash in both", "Not rated".
- `modeGraph(split, {compact})`: five colour bar per mode with a white marker at the score, grade, call; the full version adds trait pair / closest roll bars, full matches, a one line lean ("Better for PvP") and the Aegis tier.
- Where it shows: Weapons cards (compact) and new sorts `Sort: best for PvE / PvP`; weapon detail side panel (live: recomputed from the previewed perks, so the ❖ PvE/PvP god roll buttons and perk clicks update it); Look up a weapon (`lookupModes()`: rolls per mode, share bar, most wanted traits per mode, every copy you own with its compact graph, click opens detail); the roll popup (stream.js `rollHtml`, so Vault, Character, Postmaster, Activity hover); Vault rows and Activity entries (`PvE A · PvP D · Keep for PvE`); Vendors weapon cards (computed from the vendor roll); Character and Vault search (`keep for pvp`, `pve a`, phrase match).
- Activity stream: drops logged as New show the saved label (`savedLabel`) as soon as one exists. When a page sees new drops of a kind it can't rate, `bgLabel(kind)` loads that page in a hidden 1px iframe (`data-lbl`), at most one per kind and once per 3 minutes (sessionStorage `relabelAt:*`, shared with the Character page), never inside a frame and never when the token has under 5 min left. The `storage` event redraws the stream. The Character page also rescans when any item (postmaster included) has no label (`labelNew`).
- Gear tier diamonds: `tierPips(t)` / `tierIcon(imgHtml, t)` put 1 to 5 diamonds down the left of an icon (Character tiles replace the old `T5` text; Weapons, Armor, Vault, Vendors cards, roll popup, Activity rows).
- Character page also shows the Vault page's space and currency strip (`readSpace` / `spaceHtml`, money kept in `state.vmoney`).

## Speed (keep these when changing pages)

- **Cache busting:** pages reference `stream.js?v=__BUILD__`, `rating.js?v=__BUILD__`, `theme.css?v=__BUILD__`, nav links `page.html?v=__BUILD__#hash`, and the hidden labeler frames `?b=__BUILD__`. The deploy workflow replaces `__BUILD__` with the first 8 characters of the commit SHA (`sed` over `_site/*.html`, `stream.js`, `rating.js`), so the GitHub Pages CDN (10 min cache) never serves an old script with a new page. Locally the literal `__BUILD__` query is harmless. New pages, scripts or nav links must use the same placeholder.
- **Rolls without a request:** Weapons (`304,305,310` added to its profile), Vault and Character load profile components `300,304,305,310`. `trackDrops` hands the profile to `window.rollCapture`, which keeps sockets, reusable plugs, stats, instances and each item's character, clears `rollCache`, and preloads stat names (`statNames`) in idle time. `readRoll` uses that data first and only calls the single-item endpoint when the item isn't in it (Today, Vendors, Shaders, Armor pages). It draws at once from the lite manifest every page already holds (`state.defs`: name, icon, type; `LITE_CAT` maps the type text to the plug categories `SKIP_PLUG` needs), then `fullRoll()` loads the full plug and item definitions (descriptions, editable mod sockets) from IndexedDB or Bungie and redraws every open `[data-rollbox]` in place, unless a mod list is open. A perk or mod change deletes the item from `profIC` so the next read is fresh.
- Hover prefetches the roll on `mouseover` and shows the card after 140 ms (was 300 ms).
- **Account lookup cached:** `myMemberships(bungie)` (rating.js) keeps `GetMembershipsForCurrentUser` in sessionStorage `acctMe`, keyed by the last 16 characters of the token, so each page skips one round trip after the first. A new sign-in has a new token, so it can't go stale.
- **Parallel start:** Weapons starts `loadDefs()` and `loadWishlist()` (≈0.6 s to parse voltron) together with the account and profile requests and awaits them just before `buildItems`. Character, Vault, Vendors and Shaders start `loadDefs()` / `loadManifest()` alongside `getAccount()` and the profile and await it after the profile arrives.
- `<link rel="preconnect">` and `dns-prefetch` to www.bungie.net on every page; JS-built `<img>` tags use `decoding="async"`; `content-visibility:auto` on Weapons/Armor cards, Vault rows, Character All + vault cells and Activity entries.
- Measured with every Bungie request delayed 250 ms (tests/perf_roll.py, perf_load.py): roll card 1343 / 1335 / 832 ms → 344 / 241 / 223 ms (first, next item, reopen); Vault page open to items 870 → 360 ms.

## Pinned Activity panel sizing

- One CSS variable `--pinw` on `body` drives the pinned layout: 390 px at 1500 px+ screens, 330 px from 1100 to 1499, and 0 under 1100 (the panel then floats over the page). Page padding, `.modal`, `.pmpanel`, `#noticeStack`, toasts and the bulk bar use it; `placeRoll` and the Character page `place()` read it with `getComputedStyle`.
- Buttons, chips, selects and badges never wrap inside themselves; Weapons toolbar rows and the panel header wrap instead. tests/e2e_pin_layout.py checks every page at 1920 to 390 px.
- Postmaster panel: a pinned Activity panel stays open beside it; an unpinned one steps aside while the Postmaster is open and comes back when it closes (`streamWasOpen`).

## Moves (pullTo, every page)

- No fixed pauses between steps; throttling is handled by the retry in `bungieAction()`.
- Character to character: while the item goes to the vault, `pmEnsureRoom(target, hash, true, false)` frees a slot on the target at the same time (two Bungie calls in parallel), then the item goes to the target. `transfer()`'s own room check then finds the slot free.
- Activity stream Pull: the button reads "Pulling…" / "Pulling from postmaster…" right away; armor class comes from the page's lite manifest (`state.defs[h].c`) before falling back to the full definition.
- Measured with 250 ms per request (tests/perf_move.py): character to character into a full slot 1374 → 514 ms; first pull of a page 1634 → 779 ms.

## Added Nov 27 (late)

- **Inventory section** (Character and Vault, `readInventory` / `inventoryHtml` in core.js): every non-equippable storage area like the game's inventory screen: Engrams per character, Consumables, Modifications, and buckets Bungie leaves unnamed (named after the most common item type inside). Bucket names/sizes from `DestinyInventoryBucketDefinition` (`category` 3 equippable and 0 invisible are skipped, plus `INV_SKIP`: vault, postmaster, pursuits, quests, gear slots). Header `used/cap`, gold at 85%, red when full, dashed empty boxes when the cap is 21 or less. On the Vault page the Inventory follows one character (`invForChar()`): the tab picked in the Inventory header (`[data-invc]`, not saved), else the Where chip's character, else the Pull-to character, else the last played. Character buckets another character has show empty (0/cap) for this one. `inventoryHtml(sections, charName, extra)` takes optional header HTML. Vault page space strip names unnamed buckets the same way and its tooltip lists what they hold and what Full means.
- **Manual refresh** (stream.js, every page): header `#btnReload` ↻, Activity panel `#streamReload` ↻ and the R key run the page's own `scan()` (no page reload), spin while running, then redraw the Postmaster panel and stream. Postmaster panel keeps its own ↻.
- **Tap to move** (stream.js `moveBar`): the roll popup on every page shows "Move to → <character> / → Vault" for weapons and armor in `state.gear` (armor only to its class). Uses `pullTo` / `transfer` / `pullFromPostmaster`, updates the page record through `byId`, re-reads after 2 s. Hidden inside the Character page item card (`.cpop .rp-move`), which has its own buttons.
- **Weekly reward tracks** (vendors.html): vendors marked `visible: false` are read too, but only their weapons and armor with a visible roll from a Vanguard / Nightfall / Strike (→ Zavala) or Crucible / PvP (→ Shaxx) named vendor or display category are kept (`weeklyOf`), folded into that vendor's entry with `it.weekly` (badge "Weekly reward", "Earned from the weekly rewards track"). Other hidden vendors (collections previews and the like) and their random items are dropped, and they never go into `vendSales`. The scan status says how many weekly items were found or that Bungie sent none. Not yet confirmed against live data.
- **Slim god roll cache** (index.html): after a full parse, `saveSlimWishlist()` stores only the owned weapons' rolls (notes re-indexed) in IndexedDB `wlSlim` `{sig, at, covered, info, wl}`; `loadWishlist()` uses it when the list signature matches and it is under 24 h old (`state.wlSlim`). A weapon outside `covered`, Look up, or Settings → Refresh loads the full lists. Weapons page scan 855 → ~90 ms on later loads.
