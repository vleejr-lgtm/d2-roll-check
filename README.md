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
| theme.css | Shared look for every page: colors, header, spacing, cards. Keep it next to the .html files |
| stream.js | The Activity stream, shared by all three pages. Keep it next to the .html files |
| start-server.ps1 | Old http://localhost:8000 server. Works for scanning only, no sign-in |

## One time setup

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

**Gear to get** shows community PvE and PvP priority badges for each archetype (hover for why), plus **Top PvE picks** / **Top PvP picks** filters that highlight the slots where you still need a Tier 5. **Set progress** shows every set you own with PvE and PvP community tiers (or Not rated when no guide has ranked it), where it drops, and the exact 2-piece and 4-piece bonus text from Bungie. Sort it by community rank or by pieces owned. **Top sets to get** lists the top rated sets you have no pieces of, with source and the reason they rank. Duplicate old exotics are grouped with a count. These rankings are community opinion as of November 2026, not Bungie data.

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
