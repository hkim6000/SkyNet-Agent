# Pitfalls found while building SkyNet sites

Each of these broke a real build or a real page. Check the list before writing code and again before delivering.

## C#

| Problem | Rule |
|---|---|
| A server method with the same name as its class (`Search.Search()`) does not compile | Name methods after the action: `Suggest`, `Find`, `Filter` |
| A model class with the same name as a page (`Series` model, `Series` page) is ambiguous | Give models distinct names: `ComicSeries`, `Exhibit`, `GalleryEvent` |
| Two methods with the same name (a public `Pick()` endpoint and a private `Pick(string, ...)` helper) make method lookup ambiguous | Every public server method name must be unique in the class, also among private helpers |
| A page named `Calendar`, `Event` or `Helper` | `Calendar` hides `System.Globalization.Calendar` inside that file (fine); never name a page `Helper` when `codes/Helper.cs` exists |
| `await Task.CompletedTask;` | Never write it; accept the CS1998 warning |
| Unused private fields | They raise warnings; with warnings as errors the check fails. Delete them |
| `GetDataValue` / `QueryValue` may return null or "" for a missing key | Always `(GetDataValue("k") ?? string.Empty).Trim()`; use explicit flags (`only=1`) instead of "key present" |
| A text value written into `ExecuteScript("X.f('" + v + "')")` | Escape it: backslash, quote, `<`, line breaks (`JsText`), or use `JsonSerializer.Serialize` |
| Dates that look current forever | Store offsets in days (`"start": -20`) and compute `DateTime.Today.AddDays(x)`; skip closed days in code |

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
| Making text smaller to fit | Reduce padding and margins instead; keep readable font sizes |

## Hosting

| Problem | Rule |
|---|---|
| A strict Content-Security-Policy (for example `default-src 'self' 'unsafe-inline'`) blocks Google Fonts, `blob:` and `data:` images | Always give fonts a solid fallback stack; draw local previews with `createImageBitmap` on a `<canvas>` instead of `blob:` URLs |
| The site runs in a sub-folder (`/MySite/Menu`) | Use relative links (`href="Menu"`, `src="images/..."`), never root-absolute ones |
| `data/*.json` content duplicated by the Web SDK (NETSDK1022) | Use the csproj rules in project.md: `Exclude="data\**\*.json"` plus a separate `Content Update` |
