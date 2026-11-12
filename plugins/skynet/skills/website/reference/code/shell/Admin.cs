using System.Text.RegularExpressions;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class Admin : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
            SiteData site = await Store.LoadSite();
            string start = Safe(QueryValue("p"));
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_brand}", Ui.Esc(site.Brand))
                .Replace("{plhd_start}", start == string.Empty ? Access.Home : start);
        }

        private static string Safe(string? page)
        {
            string p = (page ?? string.Empty).Trim();
            return Regex.IsMatch(p, "^Admin[A-Za-z]{1,40}$") && p != "AdminLogin" ? p : string.Empty;
        }

        public async Task<ApiResponse> Open()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminJs.expired();");
                return response;
            }
            string page = Safe(GetDataValue("pg"));
            if (page == string.Empty || !Auth.CanOpen(c, page))
            {
                await Store.Log(c.U.Id, "open", page == string.Empty ? "unknown page" : page, false);
                response.SetElementContents("db-menu", await Auth.Menu("db", Access.Home, c));
                response.ExecuteScript("AdminJs.refused('" + Ui.Js(page) + "');");
                return response;
            }
            HtmlDocument doc = await PartialDocument(page);
            response.SetElementContents("db-p-" + page, doc);
            response.SetElementContents("db-menu", await Auth.Menu("db", page, c));
            response.SetElementContents("db-who", Auth.Who("db", c));
            response.ExecuteScript("AdminJs.opened('" + page + "');");
            return response;
        }

        public async Task<ApiResponse> Menu()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminJs.expired();");
                return response;
            }
            string page = Safe(GetDataValue("pg"));
            response.SetElementContents("db-menu", await Auth.Menu("db", page == string.Empty ? Access.Home : page, c));
            response.SetElementContents("db-who", Auth.Who("db", c));
            return response;
        }

        public async Task<ApiResponse> SignOut()
        {
            ApiResponse response = new ApiResponse();
            string tok = GetDataValue("tok") ?? string.Empty;
            Ctx? c = await Auth.Check(tok);
            if (c != null)
            {
                await Auth.Close(c.Tok);
                await Store.Log(c.U.Id, "sign out", c.U.Login, true);
            }
            response.ExecuteScript("AdminJs.expired();");
            return response;
        }
    }
}
