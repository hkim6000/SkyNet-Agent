# Admin and staff rights

Read this when a site has a staff area: bookings, orders, articles, a schedule, anything people sign in to manage. It is the pattern used by the hotel, newspaper and clinic templates. The site always runs on its real data; there is no demo mode.

## Shape

| Part | Files |
|---|---|
| Sign-in page | `AdminLogin` (prefix `lg-`) |
| Dashboard | `Admin` (prefix `db-`; never `ad-`, see pitfalls) |
| One page per area | `AdminBookings`, `AdminRooms`, ... |
| Always | `AdminUsers`, `AdminSettings`, `AdminActivity`, `AdminAccount` |
| Shared C# | `codes/Core/Store.cs`, `Access.cs`, `Auth.cs`, `Local.cs`, `Ui.cs` |
| Data | `data/site.json`, `data/staff.json`, `data/activity.json` |
| Run-time files | `temp/admin/sessions.json`; `appConfig/initial-admin.txt` until the first sign-in |

`codes/Core/` is the one exception to "pages are self-contained": sign-in, rights and storage must behave the same on every page, so they live in one place. Everything else (markup, CSS, JS, page methods) stays per page.


## Areas and rights

```csharp
public sealed class Area
{
    public string Key { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string Page { get; init; } = string.Empty;
    public string Extra { get; init; } = string.Empty;
    public bool AdminOnly { get; init; }
    public bool NoEdit { get; init; }
}

public static readonly Area[] Areas =
{
    new Area { Key = "bookings", Name = "Bookings", Page = "AdminBookings", Extra = "Cancel" },
    new Area { Key = "rooms", Name = "Rooms", Page = "AdminRooms" },
    new Area { Key = "activity", Name = "Activity log", Page = "AdminActivity", NoEdit = true },
    new Area { Key = "settings", Name = "Settings", Page = "AdminSettings", AdminOnly = true },
    new Area { Key = "users", Name = "Users", Page = "AdminUsers", AdminOnly = true }
};
```

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

- The menu is built on the server from the rights (`Auth.Menu`), with small count badges (unread messages, people waiting). Areas a person can't see are left out; without the activity right they get **My activity**.
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
- The browser keeps the token in a cookie (`xx_tok`, `path=` the site's base folder, `samesite=lax`). Every admin request sends it as the key `tok`; `Load` answers with the menu and the signed-in person, or `expired()` sends the browser back to `AdminLogin`.
- Changing someone's password, or switching them off, closes all their sessions. Changing your own password in My account closes your other sessions and keeps this one.
- A user with `MustChange` (the first manager, or anyone whose password a manager reset) gets no session until they choose their own password on the sign-in page.

```js
function api(method, list) {
    list = list || [];
    list.push({ key: 'tok', vlu: getCookie('xx_tok') });
    $ApiRequest('AdminRooms/' + method, JSON.stringify(list));
}
```

## First sign-in

There are no sample staff and no password in `application.cfg`. The first time the sign-in page opens and no manager has their own password yet, the site creates the user `admin` with a random password, writes it to `appConfig/initial-admin.txt`, and shows it in a box on the sign-in page, but **only to a request from the computer the site runs on** (the developer pressing F5). The first sign-in asks for a new password; then the file is deleted and the box never shows again.

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

`Program.cs` hands the request accessor to `Core/Local.cs` (the starter already registers it):

```csharp
var app = builder.Build();
MySite.Core.Local.Accessor = app.Services.GetRequiredService<IHttpContextAccessor>();
```

```csharp
using System.Net;
using Microsoft.AspNetCore.Http;

namespace MySite.Core
{
    public static class Local
    {
        public static IHttpContextAccessor? Accessor { get; set; }

        public static bool Request()
        {
            HttpContext? h = Accessor?.HttpContext;
            if (h == null)
            {
                return false;
            }
            IPAddress? ip = h.Connection.RemoteIpAddress;
            string host = h.Request.Host.Host;
            bool named = host is "localhost" or "127.0.0.1" or "[::1]" or "::1";
            return ip != null && IPAddress.IsLoopback(ip) && named && !h.Request.Headers.ContainsKey("X-Forwarded-For");
        }
    }
}
```

The address **and** the host name must both be local: behind a reverse proxy on the same machine every visitor arrives from `127.0.0.1`, but with the site's public host name, so they never see the box.

`Store`:

```csharp
public static string InitialFile => Path.Combine(Root, "appConfig", "initial-admin.txt");

public static async Task EnsureFirstManager()
{
    using (await Hold())
    {
        List<Staff> staff = await LoadStaff();
        if (staff.Any(u => u.Admin && u.Active && !u.MustChange && u.Hash != string.Empty))
        {
            return;
        }
        if (File.Exists(InitialFile) && staff.Any(u => u.Admin && u.Active && u.MustChange))
        {
            return;
        }
        string pass = Access.NewPassword();
        Staff? u = staff.FirstOrDefault(x => x.Login == "admin");
        if (u == null)
        {
            u = new Staff { Id = "u-admin", Login = "admin", Name = "Administrator", Title = "Manager" };
            staff.Insert(0, u);
        }
        u.Admin = true;
        u.Active = true;
        u.MustChange = true;
        u.Hash = Access.HashPassword(pass);
        await SaveStaff(staff);
        Directory.CreateDirectory(Path.GetDirectoryName(InitialFile) ?? Root);
        await File.WriteAllTextAsync(InitialFile, "user: admin" + Environment.NewLine + "password: " + pass + Environment.NewLine);
    }
}

public static string InitialPassword()
{
    if (!File.Exists(InitialFile))
    {
        return string.Empty;
    }
    string line = File.ReadAllLines(InitialFile).FirstOrDefault(l => l.StartsWith("password: ", StringComparison.Ordinal)) ?? string.Empty;
    return line.Length > 10 ? line.Substring(10).Trim() : string.Empty;
}
```

`Access.NewPassword()` makes 12 characters in three groups of four from `ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789` with `RandomNumberGenerator.GetInt32` (no 0/O or 1/l/I to misread).

`AdminLogin`:

```csharp
public override async Task OnInitialized()
{
    HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
    await Store.EnsureFirstManager();
    HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText.Replace("{plhd_first}", Local.Request() ? FirstBox(Store.InitialPassword()) : string.Empty);
}
```

- `SignIn`: check user name and password (with the 6-in-5-minutes pause). If the user has `MustChange`, open no session; reveal two fields *New password* and *New password again* and turn the button into **Save and sign in** (`AdminLoginJs.choose()`).
- `SetPassword`: check the user name and current password again, then the new one: 8 characters or more, different from the current one, both fields equal. Save the hash, clear `MustChange`, delete `initial-admin.txt`, log it, open the session.
- Lost the initial password before the first sign-in: delete `appConfig/initial-admin.txt` and open the sign-in page; a new one is made. Locked out of every manager account later: remove the managers from `data/staff.json` (or set `"admin": false`) and open the sign-in page.
- After deploying, open `https://<site>/appConfig/initial-admin.txt` and `https://<site>/data/staff.json` in a browser: both must answer 404. If a host serves those folders, block them in the server settings.
- `application.cfg` has no admin keys. Never commit `initial-admin.txt`, `data/staff.json` or `temp/` from a developer machine; add them to `.gitignore`.

## Storage rules

- Wrap every load-change-save in one lock: `using (await Store.Hold()) { load; change; save; }`.
- Write JSON to a temp file, then `File.Move(tmp, file, true)`.
- Log every change: `Store.Log(userId, "cancel", "WC-7G3VCG · Ava Abbott", true)`. Keep the latest 5,000 entries.
- Keep personal data to what the site needs. A clinic stores contact details and visit history, never medical notes; say so next to every free-text note field.
- Sample content (teams, services, people, products) can ship in `data/site.json` for the owner to replace. Ship no sample staff, patients, customers, orders or bookings: the site starts empty and fills with real use.

## Admin page skeleton

```csharp
public class AdminRooms : WebPage
{
    private const string AreaKey = "rooms";

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
        response.SetElementContents("rm-menu", Auth.Menu("rm", "AdminRooms", c, site));
        response.SetElementContents("rm-who", Auth.Who("rm", c));
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

Every admin page: `robots noindex, nofollow`, the same header (site name, signed-in person, View site, Sign out), the menu as a side rail that becomes a slide-in panel on tablets and phones, a toast, and one modal for editing.

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
    document.getElementById('xx-site').appendChild(askBox);
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
- Every role signs in and sees only its menu; a View user has no change buttons; a refused request appears in the log as Refused.
- Every confirm dialog: OK goes ahead; Cancel, Esc and the backdrop step back.
- After testing, delete `data/staff.json`, `data/activity.json`, `appConfig/initial-admin.txt` and `temp/admin`, so the delivered project starts clean and makes its own first password.
- The README has the permission table and the first sign-in steps.
