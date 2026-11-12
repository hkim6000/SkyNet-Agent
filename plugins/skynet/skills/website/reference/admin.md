# Admin and staff rights

Read this when a site has a staff area: bookings, orders, articles, a schedule, anything people sign in to manage. It is the pattern used by the hotel, newspaper and clinic templates. The site always runs on its real data. The only switch is the **run mode** below: Demo pre-fills the sign-in for a public showcase, Production is the real thing.

## Shape

| Part | Files |
|---|---|
| Sign-in page | `AdminLogin` (prefix `lg-`) |
| Shell | `Admin` (prefix `db-`; never `ad-`, see pitfalls): top bar, left menu, right content panel. Loads once |
| Dashboard | `AdminHome` (prefix `hd-`), the first panel |
| One page per area | `AdminBookings`, `AdminRooms`, ... Each is a **panel page**: it holds only its content and opens inside the shell |
| Always | `AdminSettings` (with Initialize data), `AdminAccount`; `AdminMessages` when there is a contact form; with several staff also `AdminUsers` and `AdminActivity` |
| Shared C# | `codes/Core/Store.cs`, `Access.cs`, `Auth.cs`, `Local.cs`, `Ui.cs`; `Media.cs` when there is a media library ([media.md](media.md)); `Blocks.cs` when pages are block-edited ([pages.md](pages.md)); `Init.cs` ([initialize.md](initialize.md)) |
| Usual areas | Orders or bookings, the catalogue, **Pages** (page text and pictures, [pages.md](pages.md)), **Media library** ([media.md](media.md)), **Messages** (the contact form inbox), Activity log, Settings, Users |
| Data | `data/site.json`, `data/staff.json`, `data/activity.json` |
| Run-time files | `temp/admin/sessions.json`; `appConfig/initial-admin.txt` until the first sign-in |

**Copy the working code, do not rewrite it.** [site/](site/REFERENCE.md) is a complete project that builds and runs as it is. `codes/Core/` holds `Store.cs`, `Access.cs`, `Auth.cs`, `Ui.cs`, `Local.cs` (and `Media.cs`, `Blocks.cs`, `Init.cs`); `codes/Models/MySiteModel.cs` holds every class the staff area needs; `Program.cs` is the full one for a site with a staff area; and there are the four files each of `Admin` (shell), `AdminHome` (dashboard), `AdminLogin`, `AdminAccount`, `AdminSettings`, `AdminMessages`, `AdminUsers` and `AdminActivity`. Start the new site from a copy of the whole folder and build it once before changing anything. All of it is tested together on the real framework. Rename the namespace `MySite`, the cookie name `ms_tok` (in `Admin.js` and `AdminLogin.js`), the colours, the fonts and the logo; change `Access.Areas` to the site's areas, and drop the Media part of Settings when there is no media library.

**The admin style kit.** Every panel's CSS starts from the same set of rules: the four `AdminMessages` files in [site/](site/REFERENCE.md) are the kit: a list with chips, search and a pager, a modal form, the confirm box and the toast, with nothing page-specific beyond the message fields (buttons, panels, fields of every input type, tables that become cards below 600px through `data-l` labels, pills). Copy all four under the new page's name and prefix, then change the fields and add the page's own rules. The brand of the whole staff area is four lines at the top of `Admin.css`: `--admin-accent`, `--admin-accent-d`, `--admin-head`, `--admin-text`, with the `@font-face` rules for the site's fonts. Every panel reads them (`--xx-accent: var(--admin-accent, ...)`), so rebranding is that one file plus `AdminLogin.css` (a page of its own). Keep the neutral greys of the panels as shipped.

`codes/Core/` is the one exception to "pages are self-contained": sign-in, rights and storage must behave the same on every page, so they live in one place. A calculation that several pages must show the same way (a price, a total, a fee) may live there too, as `Core/<Name>.cs` (for example `Core/PriceCalc.cs`). A `Core` class must never have the name of a page (`Pricing` when there is a Pricing page): SkyNet finds pages by class name (pitfalls). Everything else (markup, CSS, JS, page methods) stays per page.

## One admin or several staff

Ask in the plan: *Staff area: one admin, or several staff with roles?*

| | Several staff (default) | One admin |
|---|---|---|
| Switch | `Access.OneAdmin = false` | `Access.OneAdmin = true` |
| Rights | Letters per area per person (below) | The signed-in admin may do everything; `Access.Can` answers yes |
| Pages | Users, Activity log, Settings, My account | Settings, My account; no Users, no Activity page (the log is still written) |
| Sample staff | One account per role ([initialize.md](initialize.md)) | None |

Areas marked `StaffOnly` (Users, Activity log) disappear from the menu and are refused in one-admin mode. Every page still calls `Access.Can`, so a site can move from one admin to several staff later by changing the switch and adding the two pages.

## Admin shell

The staff area is **one page that never reloads**. `Admin` draws the top bar (brand, signed-in person, View site, Sign out) and the left menu once; the right side holds one panel per area page.

- **Menu click:** `AdminJs.open('AdminRooms')` asks `Admin/Open`. The server checks the session and the area right, then answers `response.SetElementContents("db-p-AdminRooms", await PartialDocument("AdminRooms"))`: SkyNet runs that page's `OnInitialized` and puts its HTML, CSS and JS into the panel. The top bar and menu stay; nothing flashes.
- **Opened panels stay.** Coming back to a page shows its panel at once and calls `XxJs.shown()`, which reloads its list (pitfalls: a list on screen must not go stale). A page with unsaved edits does not reload in `shown()`.
- **The address follows:** `Admin?p=AdminRooms` with `history.pushState`; Back, Forward, refresh and bookmarks open the right panel. The query name is `p`, so no page may use `p` as a request key (pitfalls).
- **Badges** (unread messages, people waiting) come from `Auth.Badges`, a function the site sets in `Program.cs`; after a change a panel calls `AdminJs.refresh()` to update them.
- **Refused or expired:** a page the person may not open is refused, logged and the dashboard shows instead; an expired session sends the browser to `AdminLogin`.
- **On tablets and phones** the left menu is a slide-in panel opened by the burger; choosing a page closes it.
- **All panels share one document.** Three things follow:
  - SkyNet sends every input on the page with every request, so a request from one panel carries the inputs of every panel already loaded. Give every input a prefixed id (`rm-f-name`), read only your own keys, and clear file inputs after an upload, or another panel's next request uploads the files again.
  - Every panel's `keydown` handler sees every key. Act on Escape only when your panel is on screen: `function here() { var r = el('xx-site-root'); return !!r && r.getClientRects().length > 0; }`.
  - Fonts are declared once, in `Admin.css` (`@font-face`, design.md); panels use the same font names through their variables.

A **panel page** (every admin page except `Admin` and `AdminLogin`):

- HTML: `<div class="xx-site" data-page="AdminRooms">` holding `<main class="xx-main" id="xx-main">`, its modal, picker and toast. No header, no menu.
- CSS: the page's variables and content styles; no `min-height: 100vh`, no shell rules.
- JS: `api()` sends `AdminJs.tok()` as `tok`; `expired()` calls `AdminJs.expired()`; it exposes `shown()`; the last lines open the shell when someone opens the page directly:

```js
if (!window.AdminJs) {
    location.replace('Admin?p=AdminRooms');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminRoomsJs.reveal);
} else {
    AdminRoomsJs.reveal();
}
```

- C#: no `Shell()`; `Load` fills `xx-main` only.

## Areas and rights

```csharp
public sealed class Area
{
    public string Key { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string Page { get; init; } = string.Empty;
    public string Group { get; init; } = string.Empty;
    public string Extra { get; init; } = string.Empty;
    public bool AdminOnly { get; init; }
    public bool NoEdit { get; init; }
    public bool StaffOnly { get; init; }
}

public static readonly Area[] Areas =
{
    new Area { Key = "bookings", Name = "Bookings", Page = "AdminBookings", Group = "Customers", Extra = "Cancel" },
    new Area { Key = "rooms", Name = "Rooms", Page = "AdminRooms", Group = "Hotel" },
    new Area { Key = "activity", Name = "Activity log", Page = "AdminActivity", Group = "Account", NoEdit = true, StaffOnly = true },
    new Area { Key = "settings", Name = "Settings", Page = "AdminSettings", Group = "Account", AdminOnly = true },
    new Area { Key = "users", Name = "Users", Page = "AdminUsers", Group = "Account", AdminOnly = true, StaffOnly = true }
};
```

`Access.cs` in [site/codes/Core/](site/codes/Core/) holds these classes; the snippet above shows the shape. `Group` is the menu heading; `StaffOnly` areas (Users, Activity log) disappear in one-admin mode.

- A person's right in an area is a string of letters: `V` view, `E` edit, `X` the area's extra right (cancel, publish, time off). `X` needs `E`; `NoEdit` areas stop at `V`; `AdminOnly` areas are for managers only. A manager (`Staff.Admin`) has `VEX` everywhere.
- `Access.Level(user, area)` returns the letters; `Access.Can(user, area, 'E')` answers yes or no. Clean the posted grid with the same rules before saving it.
- **Own records only:** link a user to a record (`Staff.ProviderId`) and tick `Own`. Every query of that area then filters to that record: schedule columns, lists, counts, badges, the dashboard.
- **Every server method checks**, never only the menu. A refused request answers with a short message and is written to the activity log with `Ok = false`:

```csharp
private static async Task<ApiResponse> Refuse(ApiResponse response, Ctx c, string action, string target, string message)
{
    await Store.Log(c.U.Id, action, target, false);
    response.ExecuteScript("AdminRoomsJs.toast('" + Ui.Js(message) + "');");
    return response;
}
```

- The menu is built on the server from the rights (`Auth.Menu`, drawn by the shell), with small count badges (unread messages, people waiting). Areas a person can't see are left out; without the activity right they get **My activity**.
- Labels that the site lets you rename (Clinician, Room, Patient) come from settings in the menu, the rights grid and the filters alike (pitfalls).
- A manager can't remove their own manager right or switch themselves off.

## Staff, passwords and sessions

```csharp
public class Staff
{
    public string Id { get; set; } = string.Empty;
    public string Login { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Hash { get; set; } = string.Empty;
    public bool Admin { get; set; }
    public bool Active { get; set; } = true;
    public bool MustChange { get; set; }
    public Dictionary<string, string> Perms { get; set; } = new Dictionary<string, string>();
}
```

- Passwords: PBKDF2-SHA256, 100,000 rounds, 16-byte salt, stored as `pbkdf2$100000$<salt>$<hash>`; compare with `CryptographicOperations.FixedTimeEquals`. At least 8 characters.
- Sign-in pauses after 6 wrong passwords for one user name in 5 minutes.
- A session is a random 16-byte hex token in `temp/admin/sessions.json` (written under a `SemaphoreSlim`, through a temp file and `File.Move`). Sessions last 8 hours and renew while the person works.
- The browser keeps the token in a cookie (`ms_tok`, renamed per site, `path=` the site's base folder, `samesite=lax`). `AdminJs.tok()` reads it; every panel request sends it as the key `tok`, and an expired session sends the browser back to `AdminLogin` (`AdminJs.expired()`).
- Changing someone's password, or switching them off, closes all their sessions. Changing your own password in My account closes your other sessions and keeps this one.
- A user with `MustChange` (the first manager, or anyone whose password a manager reset) gets no session until they choose their own password on the sign-in page.
- **Users** (managers only, [site/codes/AdminUsers.cs](site/codes/AdminUsers.cs)): add a person (name, user name, job title, Manager, Active, a right per area); the new person gets a one-time password, shown once to the manager, and chooses their own at first sign-in. **New password** does the same for someone who forgot theirs and signs them out everywhere. Untick **Active** to stop someone signing in without losing their account; **Remove** deletes it (their log entries stay, shown as *Former staff member*). Nobody can pause, demote or remove themselves, and the last active manager cannot be paused, demoted or removed.
- **Activity log** ([site/codes/AdminActivity.cs](site/codes/AdminActivity.cs)): with the activity right, everyone's entries with a person filter, Done/Refused chips and search, 25 per page; without it, the same page as **My activity** with only the person's own entries. `Store.NameOf` shows names (*Demo manager*, *System*, *Unknown user name* for a failed sign-in with a wrong user name).
- **Staff sign-in is reachable from the public site.** Every public page's footer links to **Staff sign in** (`/AdminLogin`). When the site also has customer accounts, the header's **Sign in** opens a gateway page with a customer card and a staff card ([accounts.md](accounts.md)); without customer accounts the header needs no sign-in button and the footer link is enough.

```js
function api(method, list) {
    list = list || [];
    list.push({ key: 'tok', vlu: AdminJs.tok() });
    $ApiRequest('AdminRooms/' + method, JSON.stringify(list));
}
```

## First sign-in

There is no manager account in the delivery and no password in `application.cfg` (sample staff, if any, are removed by Initialize data). The first time the sign-in page opens and no manager has their own password yet, the site creates the user `admin` with a random password, writes it to `appConfig/initial-admin.txt`, and shows it in a box on the sign-in page, but **only to a request from the computer the site runs on** (the developer pressing F5). The first sign-in asks for a new password; then the file is deleted and the box never shows again.

```
Staff sign in
+------------------------------------------------+
| First sign-in                                  |
| User name  admin                               |
| Password   tg6U-ZzSN-ZsL5                      |
| Shown only on this computer, until you choose  |
| your own password. Also in                     |
| appConfig/initial-admin.txt.                   |
+------------------------------------------------+
User name [admin        ]  Password [**********]
                [ Sign in ]
```

The starter registers the request accessor with `AddHttpContextAccessor()`; a staff site's `Program.cs` ([site/Program.cs](site/Program.cs)) also hands it to `Core/Local.cs`:

`Local.Request()` in `Core/Local.cs` answers whether the request comes from the computer the site runs on. The address **and** the host name must both be local: behind a reverse proxy on the same machine every visitor arrives from `127.0.0.1`, but with the site's public host name, so they never see the box.

`Store.EnsureFirstManager()` makes the `admin` user with a new password and writes `initial-admin.txt` when no manager has a password of their own yet; `Store.InitialPassword()` reads it back. `Access.NewPassword()` makes 12 characters in three groups of four from letters and digits that cannot be misread (no 0/O or 1/l/I). `AdminLogin.OnInitialized` runs `Init.OnStart()`, then `EnsureFirstManager()`, and fills the box only for `Local.Request()`. The code is in [site/codes/Core/Store.cs](site/codes/Core/Store.cs) and [site/codes/AdminLogin.cs](site/codes/AdminLogin.cs).

- `SignIn`: check user name and password (with the 6-in-5-minutes pause). If the user has `MustChange`, open no session; reveal two fields *New password* and *New password again* and turn the button into **Save and sign in** (`AdminLoginJs.choose()`).
- `SetPassword`: check the user name and current password again, then the new one: 8 characters or more, different from the current one, both fields equal. Save the hash, clear `MustChange`, delete `initial-admin.txt`, log it, open the session.
- Lost the initial password before the first sign-in: delete `appConfig/initial-admin.txt` and open the sign-in page; a new one is made. Locked out of every manager account later: remove the managers from `data/staff.json` (or set `"admin": false`) and open the sign-in page.
- After deploying, open `https://<site>/appConfig/initial-admin.txt` and `https://<site>/data/staff.json` in a browser: both must answer 404. If a host serves those folders, block them in the server settings.
- `application.cfg` has no admin keys. Never commit `initial-admin.txt`, a `data/staff.json` with real accounts, or `temp/` from a developer machine; add them to `.gitignore`.

## Run mode: Demo and Production

`appConfig/application.cfg` carries the switch, right after `app.app.releasedate`, and the header comment explains it:

```
***** 2. app.app.runmode : 0.Demo (staff sign-in is filled in and any user name and password signs in), 1.Production (staff sign in with their own accounts)
app.app.runmode | 0
```

Templates ship with `0` (Demo) so a public showcase works without a password; the README tells the owner to set `1` before going live. `Store.Demo()` reads the line (cache it by the file's write time) and everything else keys off it:

- **Demo:** the sign-in form is pre-filled (`demo` / `demo1234`) with a note *Any user name and password signs in as a demo manager with every right* that also lists the sample staff logins by role (*instructors maya and luis, registrar rosa … password demo1234*). A customer sign-in form is pre-filled the same way with the first sample customer and lists the others. `SignIn` accepts anything and opens a session for a built-in `u-demo` manager (`Store.DemoManager()` creates it on first use: Admin, Active, no forced password change). A real account with its correct password still signs in as itself, so the owner can test roles. The first-password box and `initial-admin.txt` are never made in Demo. Nothing is blocked: visitors can upload, edit and delete like a manager.
- **Production:** exactly the first-sign-in flow above. `Auth.Check` also refuses a session whose user is `u-demo` while the mode is `1`, so switching the file ends every demo session at once.

`Store.Demo()` in [site/codes/Core/Store.cs](site/codes/Core/Store.cs) reads `app.app.runmode` and caches it by the file's write time, so a change to the file takes effect at the next request.

Test both: in Demo, an empty form and a random pair both reach the dashboard as *Demo manager*; in Production, both are refused and `demo`/`demo1234` is refused too.

## Storage rules

- Wrap every load-change-save in one lock: `using (await Store.Hold()) { load; change; save; }`.
- Write JSON to a temp file, then `File.Move(tmp, file, true)`.
- Log every change: `Store.Log(userId, "cancel", "WC-7G3VCG · Ava Abbott", true)`. Keep the latest 5,000 entries.
- Keep personal data to what the site needs. A clinic stores contact details and visit history, never medical notes; say so next to every free-text note field.
- Sample content (teams, services, people, products) ships in `data/site.json` for the owner to replace. Sample records (orders, bookings, messages) and sample staff ship too, for the Demo, and Initialize data removes them before real use ([initialize.md](initialize.md)).

## Admin page skeleton

A panel page's server side (full examples: `AdminHome`, `AdminAccount` and `AdminMessages` in [site/](site/REFERENCE.md)):

```csharp
public class AdminRooms : WebPage
{
    private const string AreaKey = "rooms";

    public override async Task OnInitialized()
    {
        HtmlDoc.SetTitle("Rooms | Staff");
        HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
    }

    public async Task<ApiResponse> Load()
    {
        ApiResponse response = new ApiResponse();
        Ctx? c = await Auth.Check(GetDataValue("tok"));
        if (c == null)
        {
            response.ExecuteScript("AdminRoomsJs.expired();");
            return response;
        }
        SiteData site = await Store.LoadSite();
        response.SetElementContents("rm-main", Access.Can(c.U, AreaKey, 'V') ? MainHtml(c, site) : NoAccess("Rooms"));
        return response;
    }

    public async Task<ApiResponse> Save()
    {
        ApiResponse response = new ApiResponse();
        Ctx? c = await Auth.Check(GetDataValue("tok"));
        if (c == null)
        {
            response.ExecuteScript("AdminRoomsJs.expired();");
            return response;
        }
        if (!Access.Can(c.U, AreaKey, 'E'))
        {
            return await Refuse(response, c, "room", GetDataValue("id"), "You can look but not change rooms.");
        }
        using (await Store.Hold())
        {
            SiteData site = await Store.LoadSite();
            await Store.SaveSite(site);
        }
        await Store.Log(c.U.Id, "room", GetDataValue("id"), true);
        response.ExecuteScript("AdminRoomsJs.saved();");
        return response;
    }
}
```

Every panel page: `robots noindex, nofollow`, a toast, one modal for editing. The header and the menu belong to the shell.

## Confirm dialog

One per page, built on first use. Use it for every action that changes data from a list, card or detail window; see design.md for the wording rules.

```js
var askBox = null, askDone = null, askCheck = null, askBack = null;

function askParts() {
    return { h: askBox.querySelector('h2'), p: askBox.querySelector('p'), i: askBox.querySelector('input'), e: askBox.querySelector('em'), b: askBox.querySelectorAll('button') };
}

function askClose(ok) {
    if (!askBox || !askBox.classList.contains('xx-open')) {
        return;
    }
    var x = askParts(), f = askDone, v = x.i.value.trim();
    askBox.classList.remove('xx-open');
    askDone = null;
    askCheck = null;
    if (askBack && askBack.focus && document.body.contains(askBack)) {
        askBack.focus();
    }
    askBack = null;
    if (ok && f) {
        f(v);
    }
}

function askOk() {
    var x = askParts();
    var m = askCheck ? askCheck(x.i.value.trim()) : '';
    if (m) {
        x.e.textContent = m;
        x.i.focus();
        return;
    }
    askClose(true);
}

function askBuild() {
    askBox = document.createElement('div');
    askBox.className = 'xx-ask';
    askBox.innerHTML = '<div class="xx-askbox" role="alertdialog" aria-modal="true"><h2></h2><p></p><input type="text" maxlength="300" autocomplete="off"><em class="xx-err" role="alert"></em><div class="xx-askacts"><button type="button" class="xx-btn xx-btn-ghost"></button><button type="button" class="xx-btn"></button></div></div>';
    document.getElementById('xx-site-root').appendChild(askBox);
    var x = askParts();
    x.b[0].addEventListener('click', function () { askClose(false); });
    x.b[1].addEventListener('click', askOk);
    x.i.addEventListener('input', function () { x.e.textContent = ''; });
    askBox.addEventListener('mousedown', function (e) { if (e.target === askBox) { askClose(false); } });
    window.addEventListener('keydown', function (e) {
        if (!askBox.classList.contains('xx-open')) {
            return;
        }
        if (e.key === 'Escape') {
            e.preventDefault();
            e.stopPropagation();
            askClose(false);
        } else if (e.key === 'Enter' && e.target !== x.b[0]) {
            e.preventDefault();
            e.stopPropagation();
            askOk();
        } else if (e.key === 'Tab') {
            var f = [x.i, x.b[0], x.b[1]].filter(function (n) { return n.offsetParent !== null; });
            var at = f.indexOf(document.activeElement);
            e.preventDefault();
            f[(at + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
        }
    }, true);
}

function ask(o, done) {
    if (!askBox) {
        askBuild();
    }
    var x = askParts(), input = typeof o.value === 'string';
    askBack = document.activeElement;
    askDone = done;
    askCheck = o.check || null;
    x.h.textContent = o.title || '';
    x.p.textContent = o.text || '';
    x.e.textContent = '';
    x.b[0].textContent = o.no || 'Cancel';
    x.b[1].textContent = o.ok || 'OK';
    x.b[1].className = 'xx-btn' + (o.danger ? ' xx-askdel' : '');
    askBox.firstChild.classList.toggle('xx-askin', input);
    x.i.value = input ? o.value : '';
    x.i.placeholder = o.place || '';
    askBox.classList.add('xx-open');
    if (input) {
        x.i.focus();
    } else {
        x.b[o.danger ? 0 : 1].focus();
    }
}
```

```js
ask({ title: 'Cancel this appointment?', text: 'The time becomes free for others.', value: '', place: 'Reason (optional)', ok: 'Cancel appointment', no: 'Keep it', danger: true }, function (why) {
    api('Act', [{ key: 'id', vlu: id }, { key: 'act', vlu: 'cancel' }, { key: 'why', vlu: why }]);
});
```

```css
.xx-ask { position: fixed; inset: 0; z-index: 200; background: rgba(20, 20, 22, 0.55); display: none; align-items: center; justify-content: center; padding: 20px; }
.xx-ask.xx-open { display: flex; }
.xx-askbox { background: var(--xx-paper); border-radius: 12px; width: min(440px, 100%); padding: 22px 22px 18px; box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25); }
.xx-site .xx-askbox h2 { font-size: 20px; margin: 0 0 6px; }
.xx-site .xx-askbox p { margin: 0; overflow-wrap: anywhere; }
.xx-site .xx-askbox p:empty { display: none; }
.xx-askbox input { display: none; width: 100%; min-height: 44px; margin-top: 14px; }
.xx-askbox.xx-askin input { display: block; }
.xx-askacts { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
.xx-askdel { background: #B23A30; border-color: #B23A30; }
```

## Before delivering

- First sign-in from the developer's computer: the box shows `admin` and the password; the first sign-in asks for a new one; then the box and `appConfig/initial-admin.txt` are gone and the new password works.
- A request with a public host name (or through a proxy) never shows the box.
- Every role signs in and sees only its menu; a View user has no change buttons; a refused request appears in the log as Refused. In one-admin mode the menu has no Users or Activity log.
- Every confirm dialog: OK goes ahead; Cancel, Esc and the backdrop step back.
- After testing, put back the `data/` folder copied before the tests (sample staff and records ship) and delete `appConfig/initial-admin.txt`, `data/initialized.txt` and `temp/admin`, so the delivered project makes its own first password.
- The README has the permission table, the run-mode line and the first sign-in steps.
- "View site" in the admin header opens in a new tab; at 390 the header shows the burger, the brand and Sign out only (design.md).
- Sample data is in place for the Demo, and `Core/Init.cs` with the Settings button (shipped in `AdminSettings`) exist and were tested both ways ([initialize.md](initialize.md)).
- The users list shows rights in words, not letters.
- Every public footer has **Staff sign in**; in Demo both sign-in forms are pre-filled and list the sample logins; in Production both start empty.
- The shell: a menu click changes only the right panel (a value set on `window` survives), the address follows, Back and refresh open the same panel, `/AdminRooms` opened directly lands in the shell, a refused page goes back to the dashboard.
- The project root holds the starter's `LICENSE`; `app.app.releasedate` is the delivery date; the csproj carries `TheSkyLite.SkyNet` and nothing else (no pinned `System.Security.Cryptography.Pkcs`: SkyNet 1.0.10 brings the patched version itself).
