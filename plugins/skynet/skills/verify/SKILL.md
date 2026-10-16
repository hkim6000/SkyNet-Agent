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

Fails on: comments in `.cs/.js/.css`, `Task.CompletedTask`, a `{plhd_*}` in a page's HTML that its C# never replaces, HTML classes without the page prefix, duplicate or class-named server methods, real secrets in `application.cfg`, CRLF line endings. Warns when a request key is also a query-string name read by the page (see the `website` skill, pitfalls).

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

Every page at every width must report `ok`: no broken images, no horizontal overflow, no clipped text, no leftover `{plhd_*}`, no JavaScript errors and no failed requests. **Clipped text** is text that runs out of its own box or card (for example a `nowrap` email address in a narrow column) or is cut off by an `overflow: hidden` parent; the page itself may not scroll sideways, so check the widths where columns are narrowest, often 1440 and 820, not only 390. Then **look at the screenshots** (open the PNG files): check alignment, spacing, contrast, text wrapping, empty areas and overlaps. Automated checks do not see ugly layouts.

Also open pages with typical query strings (`Shop?c=botanical`, `Item?id=...`) and with a wrong one (`Item?id=zzz`): a missing record must show a friendly not-found section, never an exception.

## 5. Interaction tests

Copy `${CLAUDE_SKILL_DIR}/scripts/interact.template.js` next to the site, rewrite the steps for this site's features, and run it:

```bash
node interact.js http://localhost:5180
```

Cover every server method: filters (result count and URL), search suggestions, every form (empty submit shows server errors, valid submit shows the confirmation), carts and totals, sign-in states, modals and keyboard actions. Wait for the server with `page.waitForLoadState('networkidle')` after each action.

For a site with an admin (see `admin.md` in the `website` skill), also test: the first sign-in box shows on the developer's computer, the first sign-in forces a new password and then the box and `appConfig/initial-admin.txt` are gone; each role signs in and sees only its menu items; a View-only user has no change buttons; a refused request is logged; confirm dialogs (OK goes ahead, Cancel and Esc step back). Afterwards delete `data/staff.json`, `data/activity.json`, `appConfig/initial-admin.txt` and `temp/admin`, so the delivered site makes its own first password.

## 6. Report

| Check | Result |
|---|---|
| Source checks | ALL CLEAR / problems fixed |
| Compile | 0 errors, 0 warnings (CS1998 allowed) |
| Screenshots | pages × widths, all ok |
| Interactions | N of N pass |

Stop the app or preview server when done.
