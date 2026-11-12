using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminLogin : WebPage
    {
        public override async Task OnInitialized()
        {
            SiteData site = await Store.LoadSite();
            HtmlDoc.SetTitle("Staff sign in | " + site.Brand);
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
            await Init.OnStart();
            await Store.EnsureFirstManager();
            bool demo = Store.Demo();
            string first = string.Empty;
            if (!demo && Local.Request())
            {
                string pass = Store.InitialPassword();
                if (pass != string.Empty)
                {
                    first = "<div class=\"lg-first\"><b>First sign-in</b><dl><dt>User name</dt><dd>admin</dd><dt>Password</dt><dd>" + Ui.Esc(pass) + "</dd></dl><p>Shown only on this computer, until you choose your own password. Also in appConfig/initial-admin.txt.</p></div>";
                }
            }
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_brand}", Ui.Esc(site.Brand))
                .Replace("{plhd_first}", first)
                .Replace("{plhd_demo}", demo ? "<div class=\"lg-demo\"><p><b>Demo mode.</b> Any user name and password signs in as a demo manager with every right.</p><p>The form is filled in for you: demo / demo1234.</p></div>" : string.Empty)
                .Replace("{plhd_user}", demo ? "demo" : string.Empty)
                .Replace("{plhd_pass}", demo ? "demo1234" : string.Empty);
        }

        public async Task<ApiResponse> SignIn()
        {
            ApiResponse response = new ApiResponse();
            string login = Ui.Clip(GetDataValue("luser"), 40);
            string pass = GetDataValue("lpass") ?? string.Empty;
            if (Auth.Paused(login))
            {
                response.SetElementContents("lg-err", "Too many tries. Wait five minutes and try again.");
                return response;
            }
            List<Staff> staff = await Store.LoadStaff();
            Staff? u = staff.FirstOrDefault(x => x.Active && x.Login.Equals(login, StringComparison.OrdinalIgnoreCase));
            if (u != null && pass.Length > 0 && Access.VerifyPassword(pass, u.Hash))
            {
                Auth.Passed(login);
                if (u.MustChange)
                {
                    response.SetElementContents("lg-err", string.Empty);
                    response.ExecuteScript("AdminLoginJs.choose();");
                    return response;
                }
                string tok = await Auth.Open(u.Id);
                await Store.Log(u.Id, "sign in", u.Login, true);
                response.ExecuteScript("AdminLoginJs.signedIn('" + tok + "');");
                return response;
            }
            if (Store.Demo())
            {
                string tok = await Auth.Open("u-demo");
                response.ExecuteScript("AdminLoginJs.signedIn('" + tok + "');");
                return response;
            }
            Auth.Failed(login);
            await Store.Log(u?.Id ?? "unknown", "sign in", login, false);
            response.SetElementContents("lg-err", "The user name or password is not right.");
            return response;
        }

        public async Task<ApiResponse> SetPassword()
        {
            ApiResponse response = new ApiResponse();
            string login = Ui.Clip(GetDataValue("luser"), 40);
            string pass = GetDataValue("lpass") ?? string.Empty;
            string next = GetDataValue("lnew") ?? string.Empty;
            string again = GetDataValue("lnew2") ?? string.Empty;
            if (Auth.Paused(login))
            {
                response.SetElementContents("lg-err", "Too many tries. Wait five minutes and try again.");
                return response;
            }
            string err = string.Empty;
            string tok = string.Empty;
            using (await Store.Hold())
            {
                List<Staff> staff = await Store.LoadStaff();
                Staff? u = staff.FirstOrDefault(x => x.Active && x.Login.Equals(login, StringComparison.OrdinalIgnoreCase));
                if (u == null || !Access.VerifyPassword(pass, u.Hash))
                {
                    Auth.Failed(login);
                    err = "The user name or current password is not right.";
                }
                else if (next.Length < 8)
                {
                    err = "Use 8 characters or more for the new password.";
                }
                else if (next == pass)
                {
                    err = "Choose a password different from the one you were given.";
                }
                else if (next != again)
                {
                    err = "The two new passwords are not the same.";
                }
                else
                {
                    u.Hash = Access.HashPassword(next);
                    u.MustChange = false;
                    await Store.SaveStaff(staff);
                    if (File.Exists(Store.InitialFile))
                    {
                        File.Delete(Store.InitialFile);
                    }
                    tok = u.Id;
                }
            }
            if (err != string.Empty)
            {
                response.SetElementContents("lg-err", err);
                return response;
            }
            string session = await Auth.Open(tok);
            response.ExecuteScript("AdminLoginJs.signedIn('" + session + "');");
            return response;
        }
    }
}
