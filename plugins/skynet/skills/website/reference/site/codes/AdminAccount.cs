using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminAccount : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("My account | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminAccountJs.expired();");
                return response;
            }
            bool demo = c.U.Id == "u-demo";
            response.SetElementContents("ac-name", Ui.Esc(c.U.Name));
            response.SetElementContents("ac-login", Ui.Esc(c.U.Login));
            response.SetElementContents("ac-rights", Ui.Esc(Access.OneAdmin ? "Administrator: every page" : Access.Words(c.U)));
            response.ExecuteScript("AdminAccountJs.loaded(" + (demo ? "true" : "false") + ");");
            return response;
        }

        public async Task<ApiResponse> ChangePassword()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminAccountJs.expired();");
                return response;
            }
            if (c.U.Id == "u-demo")
            {
                response.SetElementContents("ac-err", "The demo manager has no password to change.");
                return response;
            }
            string now = GetDataValue("acur") ?? string.Empty;
            string next = GetDataValue("anew") ?? string.Empty;
            string again = GetDataValue("anew2") ?? string.Empty;
            if (Auth.Paused(c.U.Login))
            {
                response.SetElementContents("ac-err", "Too many tries. Wait five minutes and try again.");
                return response;
            }
            string err = string.Empty;
            using (await Store.Hold())
            {
                List<Staff> staff = await Store.LoadStaff();
                Staff? u = staff.FirstOrDefault(x => x.Id == c.U.Id);
                if (u == null || !Access.VerifyPassword(now, u.Hash))
                {
                    Auth.Failed(c.U.Login);
                    err = "Your current password is not right.";
                }
                else if (next.Length < 8)
                {
                    err = "Use 8 characters or more for the new password.";
                }
                else if (next == now)
                {
                    err = "Choose a password different from the current one.";
                }
                else if (next != again)
                {
                    err = "The two new passwords are not the same.";
                }
                else
                {
                    u.Hash = Access.HashPassword(next);
                    await Store.SaveStaff(staff);
                }
            }
            if (err != string.Empty)
            {
                response.SetElementContents("ac-err", err);
                return response;
            }
            await Auth.CloseAll(c.U.Id, c.Tok);
            await Store.Log(c.U.Id, "change password", c.U.Login, true);
            response.SetElementContents("ac-err", string.Empty);
            response.ExecuteScript("AdminAccountJs.changed();");
            return response;
        }
    }
}
