# D2 Roll Check: conventions for working on this repo

Personal Destiny 2 tool, run locally at `https://localhost:8443/` (`start-server-https.ps1`). It grades weapons against community wishlists, triages Armor 3.0 pieces, shows vendor stock and daily/weekly rotations, and tracks drops. No build step, no framework, no dependencies: plain HTML + vanilla JS + one shared stylesheet.

## Files

| File | Role |
|---|---|
| `index.html` | Weapons page **and** the Home view (`#home`), plus Settings, OAuth redirect handling, and Look up a weapon (`#lookup`) |
| `armor.html` | Armor triage (Armor 3.0 archetype/tier/tertiary rules, Gear to get, mods) |
| `vendors.html` | Vendors, Zavala & Shaxx panel, Xûr panel |
| `today.html` | Lost sector of the day, weekly milestones, featured activities, challenges |
| `stream.js` | Shared Activity stream, tag-menu behavior, bottom-right notices. Loaded **after** each page's inline script |
| `theme.css` | Shared visual theme. Loaded **after** each page's inline `<style>` |
| `start-server-https.ps1` | Local HTTPS server (cert, netsh binding). `start-server.ps1` is the old http fallback |

Each page is self-contained (its own inline `<script>` with helpers like `bungie()`, `ent()`, `setStatus()`, `toast()`). Helpers are copied between pages on purpose; keep the copies in sync when changing one.

## Hard rules

- **Never rename or remove element IDs, `data-*` hooks (`data-act`, `data-copy`, `data-pick`, `data-tagset`, `data-note`, `data-open`, `data-view`), or event wiring.** Restyle with classes and `theme.css`; wrap elements in new containers if needed, but keep the element and its ID.
- **Don't change localStorage/IndexedDB keys** (users' tags, notes and caches live there). Current keys:
  - localStorage: `apiKey clientId auth bungieName tags notes myRolls wlPresets wlCustom wlUrl pullChar2 autoRefresh tagLockSync stream streamMute streamPinned streamSeen known:all weaponIndex weaponSummary armorIndex armorSummary armorRule:* acct:* vendShow vendMode vendHideCipher vendChar todayChar todayOpen todayCat lsToday lsAnchor enhPerks armorMeta armorSetSort` (legacy `known:weapons`/`known:armor` are only read for migration)
  - IndexedDB cache: `manifest2` (weapons), `manifestArmor` (armor/vendors/today items), `manifestToday` (activities), `armorSetInfo` (set bonus text), `wl:<url>` (wishlists, 24 h), `ent:<Type>/<hash>` (single definitions)
- **No secrets in files.** API key, OAuth client_id and token stay in the browser's localStorage. Never commit them; the repo is public.
- **Bungie OAuth:** Public client, redirect `https://localhost:8443/` (lands on `index.html`, which reads `sessionStorage.returnTo` to go back). No refresh token; sign-in lasts about an hour.
- **Bungie action limits:** item actions (lock, transfer, equip, socket changes) are throttled (~2 socket changes/sec, sleep 300–600 ms between calls). Perk/mod changes and equips only work in orbit, a social space, or offline.
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

- Gear to get: columns `PvE` and `PvP` sit between `Stats` and the slot columns. Filter chips `All archetypes` / `Top PvE picks` / `Top PvP picks` (localStorage `armorMeta`). Top picks = every S and A archetype for that mode (owned or not), in `META_ARCH` order; slots without a Tier 5 get the `want` highlight and a count line.
- Set progress: every owned set shows `x/5`, PvE and PvP set badges (or `Not rated`), its drop source, the exact 2-piece and 4-piece bonus text, the community reason, and missing slots. Sort chips `Community rank` / `Pieces owned` (`[data-ssort]`, localStorage `armorSetSort`). Rank sort uses the active meta mode (PvE or PvP) or the better of the two. Shows 6 rows, then a `Show all` toggle.
- Bonus text: `loadSetInfo()` reads `DestinyEquipableItemSetDefinition.setPerks` (`requiredSetCount`, `sandboxPerkHash`) and resolves names/descriptions with `entMany('DestinySandboxPerkDefinition', ...)`. Cached in IndexedDB `armorSetInfo` `{version, info: {setName: [{c, n, d}]}}`, separate from `manifestArmor`. Runs after the first render, then re-renders Gear to get.
- Top sets to get (`#setWatch`, full width under the three cards): S and A sets for the active mode (or either mode) where you own 0/5, with source, badges, bonus text and reason. 8 shown, then a toggle.
- Old exotics: grouped by name and slot, `×N` badge for duplicates (`.dupn`).

## Data sources

- Bungie.net API: profile components `102,200,201,204,205,300,304,305,310,1200`; `GetVendors` (`400,401,402,300,304,305,310`, needs the vendor OAuth scope); public `/Destiny2/Milestones/`; manifest JSON tables.
- Lost sector of the day is **not** in public data: it's the lost sector a character can run at Expert/Master in `characterActivities.availableActivities` (component 204). `isLostSector()` matches "Lost Sector" in the activity name, original name, description, mode name, or activity type name (`T.act[h].at` = `activityTypeHash`, `T.atype` from `DestinyActivityTypeDefinition`). `lostFromAccount()` merges all characters (selected first), so one character having it is enough. Results are cached per daily reset in `lsToday` (non-empty only).
- Rotation fallback: when no character lists it and there is no cache, `lsProjectionHtml()` projects today's lost sector from `LS_CYCLE` (11-day order, champions, shields), anchored by `LS_DEFAULT_ANCHOR` (2025-07-06 reset = Veles Labyrinth, from published 2025 schedules). It is an estimate for Monument of Triumph, so it self-corrects: every time Bungie shows a lost sector that is in the cycle, `setLsAnchor(name, 'api')` stores localStorage `lsAnchor` `{day, name, src}`; the user can also pick today's from a select (`src: 'manual'`). Reset is 17:00 UTC (`RESET_H`). Shows today's card plus a 7-day table. Champion/shield values are the last published ones; unknown ones show "Not published". If the rotation changes, update `LS_CYCLE`.
- `manifestToday` cache has a `schema` number (`T.schema`); bump it when the cached table shape changes so users re-download.
- The Lost Sector pill always counts the daily lost sector: from any character, from the cache, or the projected one.
- Today category pills (`state.cat`, localStorage `todayCat`): All, Lost Sector, Strikes / Nightfall, Raids, Dungeons, Crucible, Weekly / Portal. `catsOf()` classifies by activity name/type/mode; "Weekly / Portal" = weekly milestones, Portal-featured, or has weekly challenges. Counts are live and respect the search box; a filter hides empty sections and scrolls to the first match.
- Xûr: schedule-based (Fri 17:00 UTC → Tue 17:00 UTC). His Strange Coin shop is in vendor data all week, so presence in the data doesn't mean he's arrived.
- Wishlists (DIM format) from `PRESETS` in `index.html`: Community (voltron), Aegis Endgame PvE, Monument PvE/PvP, optional trash list. Footer roll counts = lines starting with `dimwishlist:`.

## Testing

- Playwright scripts with mocked Bungie responses (`page.route('**/*')`, Chromium with `--disable-web-security`, pages opened from `file://`).
- Mocks serve empty bodies for wishlists other than voltron, so the footer shows **0 rolls** for Aegis/Monument in tests. That's expected; real lists parse (Aegis ≈198k rolls, Monument PvE 25, PvP 5).
- Controls inside closed drawers/tag menus aren't clickable in tests: open them first (a MutationObserver init script that sets `details.drawer` / `details.tagpop` open) or click via `element.click()`.
- Before shipping: run every page test, diff the list of element IDs against the previous build, and check screenshots with drawers closed.

## Git workflow

- `main` is protected (ruleset `protect-main`: PR required, no force push, no deletion). Work on a branch, then:
  `git checkout -b <name>` → `git add .` → `git commit -m "..."` → `git push -u origin <name>` → `gh pr create --fill` → `gh pr merge --squash --delete-branch` → `git checkout main` → `git pull`.
- Review outside PRs carefully, especially anything touching `bungie()`/`bungieAction()` or sending data to a host other than bungie.net.
- Human-facing text in the app and README: plain, direct, no dashes as punctuation, no AI filler words.
