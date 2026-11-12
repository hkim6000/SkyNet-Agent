using System.Text;
using System.Text.RegularExpressions;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminUsers : WebPage
    {
        private const string AreaKey = "users";

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Users | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        private async Task<Ctx?> Guard(ApiResponse response)
        {
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminUsersJs.expired();");
            }
            return c;
        }

        private static async Task<ApiResponse> Refuse(ApiResponse response, Ctx c, string action, string target, string message)
        {
            await Store.Log(c.U.Id, action, target, false);
            response.ExecuteScript("AdminUsersJs.toast('" + Ui.Js(message) + "');");
            return response;
        }

        private string Field(string key, int max)
        {
            return Ui.Clip((GetDataValue(key) ?? string.Empty).Replace("\r", string.Empty).Replace("\n", " "), max).Trim();
        }

        private static bool LastManager(List<Staff> staff, string id)
        {
            return !staff.Any(s => s.Id != id && s.Admin && s.Active && s.Hash.Length > 0);
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!Access.Can(c.U, AreaKey, 'V'))
            {
                await Store.Log(c.U.Id, "open", "AdminUsers", false);
                response.SetElementContents("us-main", "<div class=\"us-panel\"><h1>No access</h1><p class=\"us-hint\">Only managers can add and change staff accounts.</p></div>");
                return response;
            }
            List<Staff> staff = await Store.LoadStaff();
            response.SetElementContents("us-main", MainHtml(c, staff));
            return response;
        }

        private static string MainHtml(Ctx c, List<Staff> staff)
        {
            StringBuilder sb = new StringBuilder("<div class=\"us-ph\"><div><h1>Users</h1><p>Staff accounts and what each person may open. A new person gets a one-time password and chooses their own at first sign-in.</p></div><div class=\"us-ph-a\"><button type=\"button\" class=\"us-btn\" onclick=\"AdminUsersJs.open('')\">Add a person</button></div></div>");
            if (Store.Demo())
            {
                sb.Append("<p class=\"us-note\">Demo mode: everyone signs in as the demo manager, so these accounts are samples. In Production each person signs in with their own user name and password.</p>");
            }
            if (staff.Count == 0)
            {
                sb.Append("<div class=\"us-panel us-empty\">No staff accounts yet.</div>");
                return sb.ToString();
            }
            sb.Append("<div class=\"us-wrapt\"><table class=\"us-table\"><thead><tr><th>Person</th><th>Access</th><th>Status</th></tr></thead><tbody>");
            foreach (Staff s in staff.OrderByDescending(x => x.Admin).ThenBy(x => x.Name, StringComparer.OrdinalIgnoreCase))
            {
                string status = !s.Active ? "<span class=\"us-pill us-pill-off\">Paused</span>" : s.Hash.Length == 0 || s.MustChange ? "<span class=\"us-pill us-pill-wait\">Must choose a password</span>" : "<span class=\"us-pill us-pill-go\">Active</span>";
                sb.Append("<tr class=\"us-row\" tabindex=\"0\" onclick=\"AdminUsersJs.open('" + Ui.Js(s.Id) + "')\" onkeydown=\"if(event.key==='Enter'){AdminUsersJs.open('" + Ui.Js(s.Id) + "')}\"><td class=\"us-first\"><b>" + Ui.Esc(s.Name) + (s.Id == c.U.Id ? " <em class=\"us-you\">you</em>" : string.Empty) + "</b><small>" + Ui.Esc(s.Login) + (s.Title.Length > 0 ? " &middot; " + Ui.Esc(s.Title) : string.Empty) + "</small></td>");
                sb.Append("<td data-l=\"Access\">" + Ui.Esc(Access.Words(s)) + "</td><td data-l=\"Status\">" + status + "</td></tr>");
            }
            sb.Append("</tbody></table></div>");
            return sb.ToString();
        }

        public async Task<ApiResponse> Open()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'V'))
            {
                return await Refuse(response, c, "open user", id, "Only managers can change staff accounts.");
            }
            List<Staff> staff = await Store.LoadStaff();
            Staff? s = id.Length == 0 ? null : staff.FirstOrDefault(x => x.Id == id);
            if (id.Length > 0 && s == null)
            {
                response.ExecuteScript("AdminUsersJs.toast('That person was not found. They may have been removed.');");
                return response;
            }
            response.SetElementContents("us-mbody", FormHtml(c, s ?? new Staff { Active = true }, s == null, staff));
            response.ExecuteScript("AdminUsersJs.opened('" + Ui.Js(s == null ? "Add a person" : s.Name) + "');");
            return response;
        }

        private static string Select(string key, string cur, bool noEdit, string extra, bool off)
        {
            List<(string V, string N)> opts = new List<(string, string)> { ("", "No access"), ("V", "Look") };
            if (!noEdit)
            {
                opts.Add(("VE", "Look and change"));
                if (extra.Length > 0)
                {
                    opts.Add(("VEX", "Change, and " + extra.ToLowerInvariant()));
                }
            }
            StringBuilder sb = new StringBuilder("<select id=\"us-f-r-" + key + "\" data-k=\"r_" + key + "\"" + (off ? " disabled" : string.Empty) + ">");
            foreach (var o in opts)
            {
                sb.Append("<option value=\"" + o.V + "\"" + (o.V == cur ? " selected" : string.Empty) + ">" + Ui.Esc(o.N) + "</option>");
            }
            return sb.Append("</select>").ToString();
        }

        private static string FormHtml(Ctx c, Staff s, bool isNew, List<Staff> staff)
        {
            bool self = s.Id == c.U.Id;
            StringBuilder sb = new StringBuilder("<form class=\"us-stack\" id=\"us-form\" onsubmit=\"return AdminUsersJs.save('" + Ui.Js(s.Id) + "')\" novalidate>");
            sb.Append("<div class=\"us-grid2\"><label class=\"us-field\" for=\"us-f-name\"><span>Name</span><input type=\"text\" id=\"us-f-name\" data-k=\"name\" maxlength=\"60\" value=\"" + Ui.Esc(s.Name) + "\" autocomplete=\"off\"><em class=\"us-err\" id=\"us-e-name\"></em></label>");
            sb.Append("<label class=\"us-field\" for=\"us-f-title\"><span>Job title (optional)</span><input type=\"text\" id=\"us-f-title\" data-k=\"title\" maxlength=\"60\" value=\"" + Ui.Esc(s.Title) + "\" autocomplete=\"off\"><em class=\"us-err\" id=\"us-e-title\"></em></label></div>");
            sb.Append("<label class=\"us-field\" for=\"us-f-login\"><span>User name</span><input type=\"text\" id=\"us-f-login\" data-k=\"login\" maxlength=\"30\" value=\"" + Ui.Esc(s.Login) + "\" autocomplete=\"off\" autocapitalize=\"none\" spellcheck=\"false\"><small>2 to 30 small letters, digits, dots, dashes or underscores. They sign in with it.</small><em class=\"us-err\" id=\"us-e-login\"></em></label>");
            sb.Append("<div class=\"us-checks\"><label class=\"us-check\"><input type=\"checkbox\" id=\"us-f-admin\" data-k=\"admin\" onchange=\"AdminUsersJs.manager()\"" + (s.Admin ? " checked" : string.Empty) + (self ? " disabled" : string.Empty) + "><span><b>Manager</b><small>Every area, including Settings and Users.</small></span></label>");
            sb.Append("<label class=\"us-check\"><input type=\"checkbox\" id=\"us-f-active\" data-k=\"active\"" + (s.Active ? " checked" : string.Empty) + (self ? " disabled" : string.Empty) + "><span><b>Active</b><small>Untick to stop them signing in, without removing the account.</small></span></label></div>");
            if (self)
            {
                sb.Append("<p class=\"us-hint\">You cannot remove your own manager right or pause yourself. Change your password on My account.</p>");
            }
            sb.Append("<fieldset class=\"us-rights\" id=\"us-rights\"" + (s.Admin ? " hidden" : string.Empty) + "><legend>What they may open</legend>");
            foreach (Area a in Access.InUse().Where(x => !x.AdminOnly))
            {
                string cur = s.Perms.TryGetValue(a.Key, out string? p) ? Access.Clean(a, p) : string.Empty;
                sb.Append("<label class=\"us-right\" for=\"us-f-r-" + a.Key + "\"><span>" + Ui.Esc(a.Name) + (a.Key == "activity" ? "<small>Without it they still see their own activity.</small>" : string.Empty) + "</span>" + Select(a.Key, cur, a.NoEdit, a.Extra, false) + "</label>");
            }
            sb.Append("</fieldset><div class=\"us-acts\"><button type=\"submit\" class=\"us-btn\">" + (isNew ? "Add person" : "Save") + "</button><button type=\"button\" class=\"us-btn us-btn-ghost\" onclick=\"AdminUsersJs.closeModal()\">Cancel</button>");
            if (!isNew && !self)
            {
                sb.Append("<button type=\"button\" class=\"us-btn us-btn-ghost us-push\" onclick=\"AdminUsersJs.reset('" + Ui.Js(s.Id) + "','" + Ui.Js(s.Name) + "')\">New password</button>");
                if (!(s.Admin && s.Active && LastManager(staff, s.Id)))
                {
                    sb.Append("<button type=\"button\" class=\"us-btn us-btn-danger\" onclick=\"AdminUsersJs.drop('" + Ui.Js(s.Id) + "','" + Ui.Js(s.Name) + "')\">Remove</button>");
                }
            }
            sb.Append("</div></form>");
            return sb.ToString();
        }

        public async Task<ApiResponse> Save()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "save user", id, "Only managers can change staff accounts.");
            }
            string name = Field("name", 80);
            string title = Field("title", 80);
            string login = Field("login", 40).ToLowerInvariant();
            bool admin = GetDataValue("admin") == "1";
            bool active = GetDataValue("active") == "1";
            Dictionary<string, string> grid = new Dictionary<string, string>();
            foreach (Area a in Access.InUse().Where(x => !x.AdminOnly))
            {
                grid[a.Key] = GetDataValue("r_" + a.Key) ?? string.Empty;
            }
            Dictionary<string, string> err = new Dictionary<string, string> { { "name", string.Empty }, { "title", string.Empty }, { "login", string.Empty } };
            if (name.Length < 2 || name.Length > 60)
            {
                err["name"] = "Use 2 to 60 characters.";
            }
            if (title.Length > 60)
            {
                err["title"] = "Keep it under 60 characters.";
            }
            if (!Regex.IsMatch(login, "^[a-z0-9._-]{2,30}$"))
            {
                err["login"] = "Use 2 to 30 small letters, digits, dots, dashes or underscores.";
            }
            else if (login == "demo" || login == "system")
            {
                err["login"] = "That user name is reserved. Choose another.";
            }
            string password = string.Empty;
            string refused = string.Empty;
            Staff? saved = null;
            using (await Store.Hold())
            {
                List<Staff> staff = await Store.LoadStaff();
                Staff? s = id.Length == 0 ? null : staff.FirstOrDefault(x => x.Id == id);
                if (id.Length > 0 && s == null)
                {
                    refused = "That person was removed by someone else.";
                }
                else
                {
                    if (err["login"].Length == 0 && staff.Any(x => x.Id != id && string.Equals(x.Login, login, StringComparison.OrdinalIgnoreCase)))
                    {
                        err["login"] = "Someone already has that user name.";
                    }
                    if (s != null && s.Id == c.U.Id)
                    {
                        admin = s.Admin;
                        active = s.Active;
                    }
                    if (s != null && s.Admin && s.Active && (!admin || !active) && LastManager(staff, s.Id))
                    {
                        refused = "Keep at least one active manager. Make someone else a manager first.";
                    }
                }
                if (refused.Length == 0 && err.Values.All(v => v.Length == 0))
                {
                    if (s == null)
                    {
                        password = Access.NewPassword();
                        s = new Staff { Id = Store.NewCode("u", staff.Select(x => x.Id)), Hash = Access.HashPassword(password), MustChange = true };
                        staff.Add(s);
                    }
                    s.Name = name;
                    s.Title = title;
                    s.Login = login;
                    s.Admin = admin;
                    s.Active = active;
                    s.Perms = admin ? new Dictionary<string, string>() : Access.CleanGrid(grid);
                    await Store.SaveStaff(staff);
                    saved = s;
                }
            }
            foreach (KeyValuePair<string, string> e in err)
            {
                response.SetElementContents("us-e-" + e.Key, e.Value);
            }
            if (refused.Length > 0)
            {
                return await Refuse(response, c, "save user", login, refused);
            }
            if (saved == null)
            {
                return response;
            }
            if (!saved.Active)
            {
                await Auth.CloseAll(saved.Id, string.Empty);
            }
            await Store.Log(c.U.Id, id.Length == 0 ? "add user" : "change user", saved.Login + " · " + Access.Words(saved), true);
            List<Staff> fresh = await Store.LoadStaff();
            response.SetElementContents("us-main", MainHtml(c, fresh));
            if (password.Length > 0)
            {
                response.SetElementContents("us-mbody", PasswordHtml(saved, password));
                response.ExecuteScript("AdminUsersJs.issued('" + Ui.Js(saved.Name) + "');");
            }
            else
            {
                response.ExecuteScript("AdminUsersJs.saved('Saved');");
            }
            return response;
        }

        private static string PasswordHtml(Staff s, string password)
        {
            return "<div class=\"us-stack\"><p>Give these details to <b>" + Ui.Esc(s.Name) + "</b> in person or by phone. They choose their own password the first time they sign in. This password is shown only now.</p><dl class=\"us-kv\"><dt>User name</dt><dd><code>" + Ui.Esc(s.Login) + "</code></dd><dt>Password</dt><dd><code class=\"us-pw\" id=\"us-pw\">" + Ui.Esc(password) + "</code></dd></dl><div class=\"us-acts\"><button type=\"button\" class=\"us-btn\" onclick=\"AdminUsersJs.copy()\">Copy password</button><button type=\"button\" class=\"us-btn us-btn-ghost\" onclick=\"AdminUsersJs.closeModal()\">Done</button></div></div>";
        }

        public async Task<ApiResponse> Reset()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "reset password", id, "Only managers can give new passwords.");
            }
            if (id == c.U.Id)
            {
                return await Refuse(response, c, "reset password", id, "Change your own password on My account.");
            }
            string password = Access.NewPassword();
            Staff? s;
            using (await Store.Hold())
            {
                List<Staff> staff = await Store.LoadStaff();
                s = staff.FirstOrDefault(x => x.Id == id);
                if (s != null)
                {
                    s.Hash = Access.HashPassword(password);
                    s.MustChange = true;
                    await Store.SaveStaff(staff);
                }
            }
            if (s == null)
            {
                response.ExecuteScript("AdminUsersJs.toast('That person was not found.');");
                return response;
            }
            await Auth.CloseAll(s.Id, string.Empty);
            await Store.Log(c.U.Id, "reset password", s.Login, true);
            List<Staff> fresh = await Store.LoadStaff();
            response.SetElementContents("us-main", MainHtml(c, fresh));
            response.SetElementContents("us-mbody", PasswordHtml(s, password));
            response.ExecuteScript("AdminUsersJs.issued('" + Ui.Js(s.Name) + "');");
            return response;
        }

        public async Task<ApiResponse> Drop()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "remove user", id, "Only managers can remove staff accounts.");
            }
            if (id == c.U.Id)
            {
                return await Refuse(response, c, "remove user", id, "You cannot remove your own account.");
            }
            string refused = string.Empty;
            Staff? s;
            using (await Store.Hold())
            {
                List<Staff> staff = await Store.LoadStaff();
                s = staff.FirstOrDefault(x => x.Id == id);
                if (s != null && s.Admin && s.Active && LastManager(staff, s.Id))
                {
                    refused = "Keep at least one active manager.";
                }
                else if (s != null)
                {
                    staff.Remove(s);
                    await Store.SaveStaff(staff);
                }
            }
            if (refused.Length > 0)
            {
                return await Refuse(response, c, "remove user", id, refused);
            }
            if (s != null)
            {
                await Auth.CloseAll(s.Id, string.Empty);
                await Store.Log(c.U.Id, "remove user", s.Login, true);
            }
            List<Staff> fresh = await Store.LoadStaff();
            response.SetElementContents("us-main", MainHtml(c, fresh));
            response.ExecuteScript("AdminUsersJs.saved('" + (s != null ? "Removed" : "Already removed") + "');");
            return response;
        }
    }
}
