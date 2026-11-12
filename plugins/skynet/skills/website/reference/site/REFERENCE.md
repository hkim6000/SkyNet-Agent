# Reference site (MySite)

A complete SkyNet project with a staff area. It builds with no warnings and runs as it is; every file is real code that was tested together on the framework. Start a site that has a staff area from a copy of this folder.

Sign in at `/AdminLogin` (Demo mode: press Sign in). Sample brand: Paperhouse Prints.

## What is here

| Part | Files |
|---|---|
| Project | `MySite.csproj`, `Program.cs` (private-folder guard, upload limits, badge and media hooks), `web.config`, `appConfig/application.cfg`, `.gitignore` |
| Shared C# | `codes/Core/`: `Store`, `Access`, `Auth`, `Local`, `Ui`, `Media`, `Blocks`, `Init`; `codes/Models/MySiteModel.cs` |
| Public pages | `Home` and `About` (block-rendered, edited in Pages), `Shop`, `Contact` (ordinary pages; Contact saves to `data/messages.json`) |
| Staff shell | `Admin` (top bar, menu, panel), `AdminLogin`, `AdminHome`, `AdminAccount` |
| Staff panels | `AdminMessages`, `AdminMedia`, `AdminPages`, `AdminSettings`, `AdminUsers`, `AdminActivity` |
| Examples | `AdminThings` (ordered photo picker, floor plan check) and `Plan` (2D plan and 3D view), with `data/things.json` and `scripts/three.min.js` |
| Data | `data/site.json` (settings, items, page blocks), `data/media.json`, `data/messages.json` |

Each page is four files with the same name: `codes/X.cs`, `htmls/X.html`, `scripts/X.js`, `styles/X.css`.

## Making it your site

1. Copy the folder, build it once, then rename: `MySite` (namespace, `.csproj`, the `.dll` in `web.config`), the cookie `ms_tok` (`Admin.js`, `AdminLogin.js`), the brand, colours and fonts (public page styles; `Admin.css` top lines for the staff area; `AdminLogin.css`).
2. Set `Access.OneAdmin` and the areas in `codes/Core/Access.cs`.
3. Delete what the site does not need, all four files of each page plus its line in `Access.Areas`:
   - One admin: `AdminUsers`, `AdminActivity`.
   - No floor plan: `Plan`, `three.min.js`, the plan classes, and `CleanPlan`/`SavePlan`.
   - `AdminThings`, the `Thing` class and `data/things.json` always go, after their picker or plan code has been copied into the site's own panel.
   - No Pages editor or no media library: see pages.md and media.md.
4. Replace the sample content: `data/site.json`, `data/media.json`, `data/messages.json`, the images.
5. Add the site's own pages: `About` for a block-rendered page, `AdminMessages` for a staff panel with a list and a form.
