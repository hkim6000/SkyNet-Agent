using System.Globalization;
using System.Text;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminSettings : WebPage
    {
        private const string AreaKey = "settings";

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Settings | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        private async Task<Ctx?> Guard(ApiResponse response)
        {
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminSettingsJs.expired();");
            }
            return c;
        }

        private static async Task<ApiResponse> Refuse(ApiResponse response, Ctx c, string action, string target, string message)
        {
            await Store.Log(c.U.Id, action, target, false);
            response.ExecuteScript("AdminSettingsJs.toast('" + Ui.Js(message) + "');");
            return response;
        }

        private static string Txt(string id, string label, string value, int max, string type = "text", string hint = "")
        {
            return "<label class=\"st-field\" for=\"st-f-" + id + "\"><span>" + label + "</span><input type=\"" + type + "\" id=\"st-f-" + id + "\" data-k=\"" + id + "\" value=\"" + Ui.Esc(value) + "\" maxlength=\"" + max + "\">" + (hint != string.Empty ? "<small>" + hint + "</small>" : string.Empty) + "<em class=\"st-err\" id=\"st-e-" + id + "\"></em></label>";
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
                response.SetElementContents("st-main", "<div class=\"st-panel\"><h1>No access</h1><p class=\"st-hint\">Only managers can open Settings.</p></div>");
                return response;
            }
            SiteData site = await Store.LoadSite();
            response.SetElementContents("st-main", FormHtml(c, site));
            return response;
        }

        private static string FormHtml(Ctx c, SiteData site)
        {
            bool canE = Access.Can(c.U, AreaKey, 'E');
            bool demo = Store.Demo();
            StringBuilder sb = new StringBuilder("<div class=\"st-ph\"><div><h1>Settings</h1><p>Business details shown on every page, and limits for uploads.</p></div></div>");
            sb.Append("<form class=\"st-panel st-stack\" id=\"st-form\" onsubmit=\"return AdminSettingsJs.save()\" novalidate><fieldset class=\"st-stack st-fs\"" + (canE ? string.Empty : " disabled") + "><h2>Business</h2>");
            sb.Append("<div class=\"st-grid2\">" + Txt("brand", "Business name", site.Brand, 40) + Txt("tagline", "Tagline", site.Tagline, 80) + "</div>");
            sb.Append("<div class=\"st-grid2\">" + Txt("phone", "Phone", site.Phone, 30, "tel") + Txt("email", "Email", site.Email, 80, "email") + "</div>");
            sb.Append("<div class=\"st-grid2\">" + Txt("address", "Address", site.Address, 120) + Txt("hours", "Opening hours", site.Hours, 100) + "</div>");
            sb.Append("<h2>Media</h2>" + Txt("videomb", "Largest video upload (MB)", site.MaxVideoMb.ToString(CultureInfo.InvariantCulture), 3, "number", "1 to 100. Photos are limited to " + Media.PhotoMb + " MB.") + "</fieldset>");
            sb.Append(canE ? "<div class=\"st-acts\"><button type=\"submit\" class=\"st-btn\">Save settings</button></div>" : string.Empty);
            sb.Append("</form>");
            sb.Append("<section class=\"st-panel st-stack\"><h2>Run mode</h2><p>" + (demo ? "This site runs in <b>Demo</b> mode." : "This site runs in <b>Production</b> mode.") + " Run mode is set in appConfig/application.cfg.</p></section>");
            if (demo && c.U.Admin)
            {
                sb.Append("<section class=\"st-panel st-stack st-danger\"><h2>Initialize data</h2><p class=\"st-hint\">Removes every record made so far: messages, the activity log and all staff accounts. Settings, pages and the media library stay. The next sign-in page shows a new first password.</p><div><button type=\"button\" class=\"st-btn st-btn-danger\" onclick=\"AdminSettingsJs.initialize()\">Initialize data</button></div></section>");
            }
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
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "save settings", "settings", "Only managers can change settings.");
            }
            Dictionary<string, string> v = new Dictionary<string, string>();
            foreach (string k in new[] { "brand", "tagline", "phone", "email", "address", "hours", "videomb" })
            {
                v[k] = Ui.Line(GetDataValue(k), 300).Trim();
            }
            Dictionary<string, string> errors = new Dictionary<string, string>();
            if (v["brand"].Length < 2 || v["brand"].Length > 40)
            {
                errors["brand"] = "Use 2 to 40 characters.";
            }
            if (v["tagline"].Length > 80)
            {
                errors["tagline"] = "Keep it under 80 characters.";
            }
            if (!Ui.IsPhone(v["phone"]) || v["phone"].Length > 30)
            {
                errors["phone"] = "Enter a phone number with area code.";
            }
            if (!Ui.IsEmail(v["email"]))
            {
                errors["email"] = "Enter a valid email address.";
            }
            if (v["address"].Length < 3 || v["address"].Length > 120)
            {
                errors["address"] = "Use 3 to 120 characters.";
            }
            if (v["hours"].Length > 100)
            {
                errors["hours"] = "Keep it under 100 characters.";
            }
            if (!int.TryParse(v["videomb"], NumberStyles.Integer, CultureInfo.InvariantCulture, out int mb) || mb < 1 || mb > Media.CeilingMb)
            {
                errors["videomb"] = "Enter a number from 1 to " + Media.CeilingMb + ".";
            }
            foreach (string k in v.Keys)
            {
                response.SetElementContents("st-e-" + k, errors.TryGetValue(k, out string? e) ? e : string.Empty);
            }
            if (errors.Count > 0)
            {
                return response;
            }
            using (await Store.Hold())
            {
                SiteData site = await Store.LoadSite();
                site.Brand = v["brand"];
                site.Tagline = v["tagline"];
                site.Phone = v["phone"];
                site.Email = v["email"];
                site.Address = v["address"];
                site.Hours = v["hours"];
                site.MaxVideoMb = mb;
                await Store.SaveSite(site);
            }
            await Store.Log(c.U.Id, "save settings", "business details", true);
            response.ExecuteScript("AdminSettingsJs.saved();");
            return response;
        }

        public async Task<ApiResponse> Initialize()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!c.U.Admin)
            {
                return await Refuse(response, c, "initialize data", "settings", "Only managers can initialize the data.");
            }
            if (!Store.Demo())
            {
                return await Refuse(response, c, "initialize data", "settings", "In Production the data is initialized once, on the first start. Edit records in their own pages instead.");
            }
            if ((GetDataValue("word") ?? string.Empty).Trim() != "INITIALIZE")
            {
                response.ExecuteScript("AdminSettingsJs.toast('Type INITIALIZE to confirm.');");
                return response;
            }
            await Store.Log(c.U.Id, "initialize data", "requested from Settings", true);
            int removed = await Init.Run("Settings, by " + c.U.Name, false);
            response.ExecuteScript("AdminSettingsJs.initialized(" + removed + ");");
            return response;
        }
    }
}
