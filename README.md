# D2 Roll Check

A local page that grades your Destiny 2 weapons against several community god roll lists. You can also open any weapon to see its perks and stats like godroll.tv, save your own god roll, and (signed in) lock, pull and apply perks in game.

## Files

| File | What it does |
|---|---|
| index.html | The app |
| start-server-https.ps1 | Serves the app at https://localhost:8443 (needed for Sign in with Bungie). First run asks for admin once |
| armor.html | Armor triage: ranks every armor piece keep or trash (open from the header) |
| today.html | Today: this week's rotations, featured activities, weekly challenges and everything your character can play |
| vendors.html | Vendors and Xûr: what's worth buying this week, where each vendor is, and when stock rotates |
| vault.html | Vault: everything you own across the vault, characters and postmaster, with search and quick moves |
| character.html | Character: each character laid out like the in-game screen, with every slot's inventory shown |
| shaders.html | Shaders: every shader in the game, which ones you own, and where to get the rest |
| theme.css | Shared look for every page: colors, header, spacing, cards. Keep it next to the .html files |
| stream.js | The Activity stream, shared by all three pages. Keep it next to the .html files |
| start-server.ps1 | Old http://localhost:8000 server. Works for scanning only, no sign-in |

## Use it online

The app is hosted on GitHub Pages: **https://vleejr-lgtm.github.io/d2-roll-check/**. Friends open the link and click **Sign in with Bungie** with their own account. There is nothing to set up on their side.

How it works: the site uses one shared Bungie app. Its API key and OAuth client_id are stored as GitHub repository secrets, and the deploy workflow (`.github/workflows/pages.yml`) writes them into `config.js` on the live site only. They are never committed. On the hosted site, Settings hides the key fields and only shows the god roll lists.

One time setup (repo owner):

1. Create a Bungie app at bungie.net/en/Application for the hosted site:
   * OAuth Client Type: **Public**
   * Redirect URL: `https://vleejr-lgtm.github.io/d2-roll-check/`
   * Origin Header: `https://vleejr-lgtm.github.io`
   * Scope: the same three as below
2. Save the key and client_id as repo secrets (`gh secret set BUNGIE_API_KEY` and `gh secret set BUNGIE_CLIENT_ID`, each prompts for the value).
3. Switch Pages to deploy from the workflow: `gh api -X PUT repos/vleejr-lgtm/d2-roll-check/pages -f build_type=workflow`.
4. Every merge to `main` redeploys. To change the key, update the secret and re-run the workflow (`gh workflow run "Deploy site"`).

The key can still be read from the live site in a browser, which is how every Bungie web app works. It only works from the app's Origin, and nobody can touch an account without signing in with it.

Tags, notes and sign-in are saved per browser, so each friend's tags stay their own.

Bungie sign-ins last about an hour. After you've signed in once, the site renews it for you: when it runs out it takes a quick trip through bungie.net and comes straight back (no Approve screen, as long as you're still logged in to bungie.net). It never does this in the middle of a scan or in a background tab. Sign out turns it off.

## One time setup (run it on your PC)

1. Bungie app (bungie.net/en/Application, open your D2 Roll Check Local app):
   * OAuth Client Type: **Public**
   * Redirect URL: `https://localhost:8443/`
   * Scope: check **Read your Destiny 2 information**, **Read your Destiny 2 vendor and advisor information** (for the Vendors page) and **Move or equip Destiny gear and other items**
   * Origin Header: `https://localhost:8443`
   * Save Changes. Copy the **API Key** and the **OAuth client_id**.
2. Run `powershell -ExecutionPolicy Bypass -File .\start-server-https.ps1`. Accept the one admin prompt. It creates a certificate for localhost, trusts it on this PC, and binds it to port 8443. Remove it any time with `-Uninstall`.
3. In the app, open Settings, paste the API key and client_id, Save.
4. Click **Sign in with Bungie**, approve on bungie.net, and the app scans your weapons.

Sign-in lasts about an hour (Bungie gives this kind of app no refresh token). Click Sign in again when it expires.

## Using it

* **Home** (click D2 ROLL CHECK in the header): connection status, weapon and armor counts from your last scans, shortcuts to every page, recent drops, and reset clocks.

* **Cards**: verdict with its mode (`GOD ROLL · PvE`, `GOD ROLL · PvE + PvP`, `CLOSE · PvP`), score, Aegis tier, perks to swap, and duplicates ranked. The PvE + PvP / PvE only / PvP only dropdown re-grades every card for that mode.
* **Click a card**: full detail view like godroll.tv. Perk columns are labeled (Barrel, Magazine, Perk 1, Perk 2, Origin) with an Enhanced toggle; a Mods grid and a Masterwork list preview their stat changes live. Hover anything for details. Mod and masterwork picks only preview stats; Apply changes perks only. **❖ PvE god roll** / **❖ PvP god roll** select a whole recommended roll in one click (click again for the next one, with which lists recommend it), and **★ My god roll** loads yours. The masterwork list only shows stats the weapon has.
  * **Save as My god roll**: your pick wins over the lists for every copy of that weapon.
  * **Apply selected perks in game**: switches the perks on that copy (only perks the copy has). Works in orbit, a social space, or offline.
  * **Lock / Unlock**, **Pull to character**, **DIM tag**.
* **Card buttons**: tag, Lock/Unlock, Pull, To vault, Apply god roll perks.
* **Lock all god rolls** / **Lock everything tagged favorite**: bulk lock.
* **Look up a weapon** tab: open any weapon's perk grid and save My god roll before you even own it.

## Tags and DIM

DIM keeps tags on its own servers and doesn't let outside apps write them. Tags you set here are saved in this browser. Click **Export DIM tags (CSV)**, then in DIM: Settings, Spreadsheets, **Import tags/notes from CSV**.

## God roll lists (Settings)

| List | Updated | Notes |
|---|---|---|
| DIM Community (voltron) | Aug 2026 | Broad, many creators, PvE + PvP |
| Aegis Endgame PvE | Oct 2026 | Strict, S to F weapon tiers |
| Giggletwig Monument PvE / PvP | Nov 2026 | Small, current meta |
| Giggletwig trash list | 2026 | Off by default. Marks D/E/F tier weapons as trash |

Monument of Triumph (June 2026) was Destiny 2's final content update, so these lists are effectively current.

## Armor triage (armor.html)

Open **Armor triage** in the header. It reads every armor piece and judges its raw roll (mods, masterwork and tuning are removed first).

* **Duplicates**: pieces with the same class, slot, set, archetype and tertiary stat are grouped. The best (higher tier, then total, then power) is kept, the rest are trash.
* **Outclassed**: Tier 1 and 2 pieces are trash when you own a Tier 4+ of the same class, slot and archetype.
* **Exotics**: duplicate copies of the same exotic keep only the best. Exotic class items are marked Review (judge their perks yourself).
* **Legacy** (pre Edge of Fate, no archetype): flagged, optionally trash.
* **Locked** pieces are never trashed unless you untick that rule.

**Gear to get** shows community PvE and PvP priority badges for each archetype (hover for why), plus **Top PvE picks** / **Top PvP picks** filters that highlight the slots where you still need a Tier 5. **Set progress** lists every set you own in two short lines: name, piece count, 2-piece or 4-piece status and PvE/PvP tiers, then missing slots and source. Hover a set name for its bonus text. Sort by community rank or pieces owned, type to filter, or show only incomplete or 4-piece ready sets. **Top Community Sets** sits next to it and ranks the top PvE and PvP sets with their source, the main reason they rank, and how many pieces you already have. Old exotics are grouped by slot, with duplicates shown as a count. The "Slots with no Tier 5" note only appears when a slot is missing one. These rankings are community opinion as of November 2026, not Bungie data.

Trash gets a suggested **junk** tag. Use tick boxes, bulk select, Lock all keepers, Pull/To vault, and Export DIM tags the same way as weapons. When your vault is clean, open D2ArmorPicker from the header to build loadouts.

## Activity stream (every page)

Click **📡 Activity** in the header. Every refresh compares your whole inventory with the last one, so weapon and armor drops both show up no matter which page you're on. Drops for the page you're on get their verdict right away. The others show as **New** with Pull and Lock buttons, plus a link that opens the item on its own page (where it gets rated, and the stream entry updates).

## Vendors and Xûr (vendors.html)

Needs Sign in with Bungie (Bungie only shares vendor stock with you signed in), plus the vendor scope above. If you added the scope after signing in, sign in again.

* **Every vendor** for the character you pick, with the landing zone Bungie lists for them (📍) and a countdown to when their stock rotates.
* **Buy / Maybe / Have it / Skip / Unrated** on each item:
  * Weapons: checked against your wishlists and My god rolls, then against what you own (open the Weapons page once so it knows).
  * Armor: Tier 5 is Buy, Tier 4 is Maybe, lower is Skip, and anything you already own at the same tier, archetype and tertiary is Have it (open Armor triage once so it knows).
* **Skipped**: items that roll their perks or stats when you buy them can't be judged, so they're listed at the bottom instead of rated.
* **Exotic Cipher** items are hidden by default. Untick the box to see them.
* **Zavala and Shaxx** have their own panel. It tells you straight out what gear to grab from each one. If one of them only has random rolls that week (Shaxx often does), it says so and tells you to skip him unless you're farming a specific roll.
* **Xûr** has his own panel at the top: arrives every Friday at reset (17:00 UTC), leaves at the Tuesday reset. His arrival follows that schedule, because his Strange Coin shop at Eternity shows up in Bungie's data all week. While he's here it lists his gear, exotics and engrams first (bounties and materials go in a fold). When he's gone it counts down to his next visit, and his all-week coin shop sits in a fold. The page reloads vendors by itself when stock rotates or Xûr arrives.

## Vault (vault.html)

* Everything you own in one list: vault, each character, what's equipped and the postmaster, with totals at the top.
* Vault space at a glance: used and free slots for the vault, consumables and modifications, with bars that turn gold when it's getting full and red when it's nearly full, plus your Glimmer, Bright Dust and other currencies.
* Search with plain words, and every word has to match: `hand cannon`, `exotic rocket`, `t5 titan`, `vault locked`. Press `/` to jump to the search box.
* Filter by where it is and what it is (weapons, armor, mods and shaders, materials, cosmetics, quests), and sort by type, name, power, rarity or location.
* Hover a weapon or armor piece (or tap it on a phone) to see its roll like DIM: stats, frame, and each perk column with the other perks you can pick. Click one of those to switch to it, or click a mod (weapon or armor) to pick any mod you've unlocked for that slot. Works in orbit, a social space or offline.
* Signed in, each weapon and armor piece has Pull (to the character in the Pull to menu), Vault and Lock buttons.

## Character (character.html)

* Pick a character at the top. You get the in-game Character screen: emblem, name, power and stats, weapons and ghost on the left, armor on the right.
* Every slot is expanded: the equipped item plus everything else that character carries for that slot, with empty boxes for free space.
* Click an item to Equip it, send it to the Vault, move it to another character, or lock it.
* Click an empty box to bring something from the vault into that slot. It only lists items that fit, and you can filter them.
* The character's postmaster sits above the slots as 21 boxes, like in game. Click an item to see its roll and pull it.
* Clicking any item also shows its roll, and you can switch perks right there.

## Activity stream

New drops show in 📡 Activity on every page, and Pull and Lock work from any page.

## Full slots

Moving an item from the vault to a character works like the postmaster now: if that slot is full, the site first moves the lowest rarity, lowest power **unlocked** item in that slot to the vault, then makes the move. Locked and equipped items are never touched. The Make room checkbox in the 📬 panel turns this on or off.

## Postmaster (every page)

* The 📬 button in the header shows how many lost items are waiting across your characters. Like DIM, it turns amber at ALMOST FULL! (15 of 21) and red at FULL! (21 of 21), and the site tells you once when a character gets there. Past 21, new drops are lost.
* Open it to pull one item or everything for a character, or send them straight to the vault (Vault / All to vault). The game has no direct postmaster to vault move, so the site pulls the item to that character and then vaults it for you. Engrams and quest items can't go to the vault. Hover a weapon or armor piece (or tap it on a phone) to see its roll: perks and stats.
* **Make room** (on by default): if that slot on the character is full, it first moves your lowest rarity, lowest power **unlocked** item in that slot to the vault, then pulls. Locked and equipped items are never moved, so lock anything you want to keep on the character. Engrams and quests can't go to the vault, so for those it tells you to clear space in game. The same applies to the 📬 Pull button on weapon, armor and vault cards.

## Shaders (shaders.html)

* Lists every collectible shader from Bungie's game data, with its swatch, name and where it comes from.
* Signed in, it reads your Collections and marks each one Owned or Need to get, with totals and your completion percentage at the top. Signed out you can still browse and search.
* Search by name or source, filter by status and by source (Ada-1 / Eververse, Vanguard / Nightfall, Crucible, Gambit, Raids & Dungeons, Events, World & Destination), and sort by newest, name, owned first or missing first.
* Click a shader for a larger swatch, how to get it, its season, and whether a vendor is selling it right now. The vendor check uses the last vendor load on the Vendors & Xûr page, so open that page once to turn it on.

## Today (today.html)

A page like todayindestiny.com, built from Bungie's own data.

* **Reset clocks**: daily reset, weekly reset, and Xûr's arrival or departure.
* **Lost Sector today**: the daily rotating lost sector, with its Expert/Master difficulties and power, champion and shield modifiers, rewards (like the exotic armor slot) and location. Bungie only lists this rotation in your character's activities, so it needs Sign in once per day; after that it still shows when you're signed out until the next daily reset.
* **This week**: the weekly rotations (Nightfall, featured raid and dungeon, events) with their modifiers, challenges and when they end. Works without signing in.
* **Signed in**, for the character you pick:
  * **Featured right now**: what the Portal is spotlighting.
  * **Weekly challenges**: your progress on each, finished ones faded.
  * **Everything you can play**, grouped by type (Raid, Dungeon, Lost Sector, Crucible...), with modifiers, power level, location and rewards.
* **Search** across activity names, modifiers, rewards and places, plus category pills with live counts: Lost Sector, Strikes / Nightfall, Raids, Dungeons, Crucible, Weekly / Portal.
* Today's lost sector is checked on all your characters, so one character having it unlocked is enough. Lost sectors rotate at the daily reset, 17:00 UTC (9 AM Pacific in winter). Bungie hides the day's lost sector on characters that haven't cleared it on normal, so when none of yours list it the page projects today's from the rotation order, with champions, shields and a 7-day preview. The projection corrects itself whenever Bungie shows the real one, or you can pick today's from the list.

The first visit downloads Bungie's activity definitions once (cached after that). Rotations reload by themselves at reset.
