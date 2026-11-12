using System.Text;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminHome : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Dashboard | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminHomeJs.expired();");
                return response;
            }
            SiteData site = await Store.LoadSite();
            Dictionary<string, int> counts = Auth.Badges == null ? new Dictionary<string, int>() : await Auth.Badges(c);
            StringBuilder sb = new StringBuilder();
            sb.Append("<div class=\"hd-ph\"><h1>Hello, " + Ui.Esc(c.U.Name) + "</h1><p>" + Ui.Esc(site.Brand) + " · " + DateTime.Now.ToString("dddd, MMMM d", Ui.Us) + "</p></div><div class=\"hd-tiles\">");
            foreach (Area a in Access.InUse().Where(a => Auth.CanOpen(c, a.Page)))
            {
                int n = counts.TryGetValue(a.Key, out int v) ? v : 0;
                sb.Append("<a class=\"hd-tile\" href=\"Admin?p=" + a.Page + "\" onclick=\"return AdminHomeJs.go(event, '" + a.Page + "')\"><b>" + Ui.Esc(a.Name) + "</b><small>" + (n > 0 ? Ui.Count(n, "item waiting", "items waiting") : "Open") + "</small></a>");
            }
            sb.Append("</div>");
            response.SetElementContents("hd-main", sb.ToString());
            return response;
        }
    }
}
