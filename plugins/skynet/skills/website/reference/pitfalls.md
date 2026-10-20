# Pitfalls found while building SkyNet sites

Each of these broke a real build or a real page. Check the list before writing code and again before delivering.

## C#

| Problem | Rule |
|---|---|
| A server method with the same name as its class (`Search.Search()`) does not compile | Name methods after the action: `Suggest`, `Find`, `Filter` |
| A model class with the same name as a page (`Member` model, `Member` page) | It compiles, but SkyNet finds pages by class name across the whole project, so the page answers `not found : MySite.Models.Member/`. Give models distinct names: `ClubMember`, `Coach`, `ComicSeries`. The `verify` source check fails on it |
| Two methods with the same name (a public `Board()` endpoint and a private `Board(Ctx, ...)` helper) make method lookup ambiguous | It compiles, but the request fails at run time. Every public server method name must be unique in the class, also among private helpers: name helpers `BoardHtml`, `PanelHtml` |
| A page named `Calendar`, `Event` or `Helper` | `Calendar` hides `System.Globalization.Calendar` inside that file (fine); never name a page `Helper` when `codes/Helper.cs` exists |
| `await Task.CompletedTask;` | Never write it; accept the CS1998 warning |
| Unused private fields | They raise warnings; with warnings as errors the check fails. Delete them |
| `GetDataValue` / `QueryValue` may return null or "" for a missing key | Always `(GetDataValue("k") ?? string.Empty).Trim()`; use explicit flags (`only=1`) instead of "key present" |
| A text value written into `ExecuteScript("X.f('" + v + "')")` | Escape it: backslash, quote, `<`, line breaks (`JsText`), or use `JsonSerializer.Serialize` |
| `DataPath` used as a folder in a server method | During a button click (an API request) `DataPath` is a web address (`https://host/app/data`), not a folder, so `File.*` on it throws. Build file paths from the app folder: `Path.Combine(Directory.GetCurrentDirectory(), "data")` |
| Dates that look current forever | Store offsets in days (`"start": -20`) and compute `DateTime.Today.AddDays(x)`; skip closed days in code |
| A global regex rename (`Service` to `CareService` to avoid a page/model clash) | It also renames properties and strings that merely contain the word. Rename the class declaration and its type uses only, then compile and grep the result |
| Counts glued to a plural noun (`n + " visits"`) | Shows "1 visits". Choose the word by the number: `n + (n == 1 ? " visit" : " visits")` |
| A site with editable words (Doctor / Dentist / Vet, Patient / Client) | One hard-coded label slips through (a rights grid, a filter, a heading). Read every label from the settings through one lookup, and grep the default word in `codes/`, `htmls/` and `scripts/` before delivering |
| A first password or staff file in a folder the web server serves | Anyone can download it. Keep `initial-admin.txt` in `appConfig/`, show it only to local requests (address and host name both local), and check after deploying that `/appConfig/initial-admin.txt` and `/data/staff.json` answer 404 |

## JavaScript and core.js

| Problem | Rule |
|---|---|
| A request key equal to a query-string name (`?q=` and key `q`) | The core sends URL params too; use different keys (`term`, `ex`, `mon`) |
| Script runs before the DOM exists | Page JS is in `<head>`; do start-up work in `reveal()` after `DOMContentLoaded` |
| A file input keeps its files | Clear `input.value` after reading, or every later request re-uploads them |
| `localStorage` can throw (private mode, blocked storage) | Wrap every read and write in `try/catch` with an in-memory fallback |
| A cookie set on `/` collides between sites on one domain | Set `path=` to the app's base folder (`location.pathname` without the page name) |
| `history.replaceState` with the wrong base | Use relative page URLs: `history.replaceState(null, '', 'Menu?c=x')` |

## CSS and layout

| Problem | Rule |
|---|---|
| `backdrop-filter`, `transform` or `filter` on the sticky header | They make a containing block: a `position: fixed` slide-in menu inside the header becomes header-sized. Keep the header plain |
| `.site h2 { margin: 0 }` beats `.mt { margin-top: 40px }` | Element-plus-class outranks a single class; write `.site .mt` |
| Two pages' features share a class name (`-sel`, `-dots`, `-step`, `-open`) | One CSS file is shared by all of a page's features; give every feature a unique class name |
| Visually hidden radio inputs (`position: absolute`) with no positioned parent | They can stretch the page sideways; give the label `position: relative` and the input `left: 0; top: 0; width: 1px; height: 1px` |
| A grid with `align-items: start` that becomes a flex column on phones | Reset to `align-items: stretch` in the media query |
| Horizontal overflow on phones | Long words, wide tables and chip rows: use `minmax(0, 1fr)`, `overflow-x: auto` on wrappers and `flex-wrap` |
| A page prefix or id that looks like an advert (`ad-`, `ads-`, `ad-main`, `banner-ad`, `sponsor`) | Ad blockers hide it (`display: none`): the page is blank for visitors with an ad blocker, while localhost and other browsers look fine. Never use `ad` as a prefix; an Admin page uses `db-` or `adm-` |
| Making text smaller to fit | Reduce padding and margins instead; keep readable font sizes |
| A base reset `.xx-site button { font: inherit; }` | Element-plus-class outranks `.xx-btn` and wipes button styles. Wrap base resets in `:where()`: `:where(.xx-site) :where(button, input, select, textarea) { font: inherit; }` |
| The header's right side grows when someone signs in (name chip, tier badge, "My classes") | Signed-out checks pass while the signed-in header runs past the screen at 1180 to 1500 px. Check pages signed in too (`STATE` in `shots.js`); at middle widths hide the name and keep the badge, and trim nav padding |
| Shared parts (header, footer) and a form using the same id (`-cname` for the footer's center name and the card form's name on card) | The server fills the wrong one and the form field cannot be typed into. Give shared parts ids that name their place (`-fname`, `-copyname`); `verify` reports duplicate ids |
| The shop name is hidden or cut to "Petalbo…" in the header at 390px | The brand is part of the layout, not decoration. On phones shorten the other side first (hide the role line, the "View site" link, menu text), keep the name on one line with `min-width: 0; overflow: hidden; text-overflow: ellipsis` only as the last resort, and check the public and the admin header at 390 |
| `white-space: nowrap` on a link (email, phone) inside a narrow grid card | It defeats `overflow-wrap: anywhere`; the text runs out of its card at desktop widths while the page itself does not scroll sideways, so page-level checks pass. Let long text wrap, or give the card a full row |

## Hosting

| Problem | Rule |
|---|---|
| A strict Content-Security-Policy (for example `default-src 'self' 'unsafe-inline'`) blocks Google Fonts, `blob:` and `data:` images | Always give fonts a solid fallback stack; draw local previews with `createImageBitmap` on a `<canvas>` instead of `blob:` URLs |
| The site runs in a sub-folder (`/MySite/Menu`) | Use relative links (`href="Menu"`, `src="images/..."`), never root-absolute ones |
| `data/*.json` or `temp/*.json` content duplicated by the Web SDK (NETSDK1022) | Use the csproj rules in project.md: `Exclude="...\**\*.json"` plus a separate `Content Update`, for `data` **and** `temp`. The `temp` case shows up only after the first staff sign-in writes `temp/admin/sessions.json` |
| Hosted card checkout (Stripe Checkout style) confirmed only when the customer comes back | A customer who pays and closes the tab is charged, and the site still marks the order unpaid and later cancels it. Confirm payment with the provider's signed webhook, and before auto-cancelling any unpaid card order ask the provider for the session's status first. Never expire a paid order |
