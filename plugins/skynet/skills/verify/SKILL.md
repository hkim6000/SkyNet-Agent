---
name: verify
description: Verify a SkyNet website before delivering it - compile with warnings as errors, check sources (comments, placeholders, CSS prefixes, request-key collisions, config secrets), screenshot every page at 1440/820/390 for overflow and broken images, and run interaction tests. Use after building or changing any SkyNet page, or when the user runs /skynet:verify.
argument-hint: "[site folder]"
---

# Verify a SkyNet site

Target folder: `$ARGUMENTS` (default: the current project folder, the one that holds the `.csproj`).

Run every step. Fix what fails, then run the failing step again. Report the results in a short table; never claim a check passed without running it.

## 1. Source checks

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_sources.py <site>
```

Fails on: comments in `.cs/.js/.css`, `Task.CompletedTask`, a `{plhd_*}` in a page's HTML that its C# never replaces, HTML classes without the page prefix, duplicate or class-named server methods (a public endpoint and a private helper with one name included), a page that shares its name with any other class (a `Member` model next to a `Member` page: SkyNet answers `not found`), real secrets in `application.cfg`, CRLF line endings. Warns when a request key is also a query-string name read by the page (see the `website` skill, pitfalls).

## 2. Compile

With the .NET SDK and NuGet access (normal case):

```bash
dotnet build <site> -p:TreatWarningsAsErrors=true -p:WarningsNotAsErrors=CS1998
```

Without NuGet access (offline sandboxes), compile against the bundled SkyNet stub instead. It checks the C# compiles against SkyNet's public API, and builds a runner used by the preview server:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/stub_check.sh <site> <RootNamespace>
```

## 3. Run the site

Normal case: start the real app and wait until it answers.

```bash
cd <site> && dotnet run --urls http://localhost:5180 > /tmp/skynet-run.log 2>&1 &
curl --retry 30 --retry-delay 1 --retry-connrefused -s -o /dev/null http://localhost:5180/
```

Offline case: serve the pages through the stub runner. The preview server renders each page with the page class and answers `$ApiRequest` calls with a small mock of `skynet.core.js` (it does not send URL parameters or form inputs automatically, so step 1's key-collision warnings matter).

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preview_server.py <site> <runner-path-printed-by-stub_check> 8190 <RootNamespace> &
```

The app and the preview server read the page list and the compiled C# when they start. After adding a page or changing C#, rebuild and restart them, or the new page answers 404 and old code keeps running. Stop them by process id (`kill <pid>`), never with `pkill -f <pattern>`: the pattern also matches the shell running the command and kills it.

## 4. Screenshots and layout

Install once, in the folder you run the scripts from (the sites folder) or globally: `npm i playwright` and `npx playwright install chromium` (or set `CHROMIUM_PATH` to an existing Chromium). The scripts look for Playwright in the current folder, then `NODE_PATH`.

```bash
node ${CLAUDE_SKILL_DIR}/scripts/shots.js http://localhost:5180 Home,Shop,Contact 1440,820,390 shots
```

Every page at every width must report `ok`: no broken images, no horizontal overflow, no clipped text, no duplicate element ids, no leftover `{plhd_*}`, no JavaScript errors and no failed requests. **Clipped text** is text that runs out of its own box or card (for example a `nowrap` email address in a narrow column) or is cut off by an `overflow: hidden` parent; the page itself may not scroll sideways, so check the widths where columns are narrowest, often 1440 and 820, not only 390. Then **look at the screenshots** (open the PNG files): check alignment, spacing, contrast, text wrapping, empty areas and overlaps. Automated checks do not see ugly layouts.

**Signed in, too.** Headers and pages change when a member or staff user is signed in (a name chip, a tier badge, "My classes"), and that is where overflow hides. In the interaction script, sign in and save the session with `await ctx.storageState({ path: 'signed-in.json' })`, then run the same pages again with it:

```bash
STATE=signed-in.json node ${CLAUDE_SKILL_DIR}/scripts/shots.js http://localhost:5180 Home,Account 1440,1320,1180,820,390 shots-in
```

Check the widths between the desktop and the tablet layout (1320, 1180) as well: a signed-in header is widest just before the menu folds. At 390 look at the header itself: the shop name must be visible and not cut to "Petalbo…", on the public pages and in the admin.

Also open pages with typical query strings (`Shop?c=botanical`, `Item?id=...`) and with a wrong one (`Item?id=zzz`): a missing record must show a friendly not-found section, never an exception.

## 5. Interaction tests

Copy `${CLAUDE_SKILL_DIR}/scripts/interact.template.js` next to the site, rewrite the steps for this site's features, and run it:

```bash
node interact.js http://localhost:5180
```

Cover every server method: filters (result count and URL), search suggestions, every form (empty submit shows server errors, valid submit shows the confirmation), carts and totals, sign-in states, modals and keyboard actions. Wait for the server with `page.waitForLoadState('networkidle')` after each action. After opening each modal or form that the server fills in, call `dupIds(page)`: an id used twice (a footer and a form field, say) makes the server write into the wrong element.

The offline preview server also catches pages that real SkyNet cannot find: a page name shared with another class, or a request method that has a private helper with the same name, fails in the runner with `not found` or `ambiguous`, as on a real server.

For a site with an admin (see `admin.md` in the `website` skill), also test both run modes: with `app.app.runmode | 0` the sign-in is pre-filled and an empty or random pair reaches the dashboard as the demo manager; with `1` both are refused. In Production: the first sign-in box shows on the developer's computer, the first sign-in forces a new password and then the box and `appConfig/initial-admin.txt` are gone; each role signs in and sees only its menu items; a View-only user has no change buttons; a refused request is logged; confirm dialogs (OK goes ahead, Cancel and Esc step back). Afterwards delete `data/staff.json`, `data/activity.json`, `appConfig/initial-admin.txt` and `temp/admin`, so the delivered site makes its own first password. With a media library (`media.md`) run its "Before delivering" list, and with block-edited pages (`pages.md`) theirs: a moved block changes the public page after Save, a bad link is refused, Restore brings a version back.

## 6. Report

| Check | Result |
|---|---|
| Source checks | ALL CLEAR / problems fixed |
| Compile | 0 errors, 0 warnings (CS1998 allowed) |
| Screenshots | pages × widths, all ok |
| Interactions | N of N pass |

Stop the app or preview server when done.
