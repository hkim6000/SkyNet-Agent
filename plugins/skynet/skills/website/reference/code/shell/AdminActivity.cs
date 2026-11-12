using System.Text;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminActivity : WebPage
    {
        private const string AreaKey = "activity";
        private const int Size = 25;

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Activity log | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        private async Task<Ctx?> Guard(ApiResponse response)
        {
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminActivityJs.expired();");
            }
            return c;
        }

        private static string Pager(int page, int pages, int total)
        {
            return "<div class=\"al-pager\"><span>Page " + page + " of " + pages + " &middot; " + Ui.Count(total, "entry", "entries") + "</span><div><button type=\"button\" class=\"al-btn al-btn-ghost al-btn-sm\"" + (page <= 1 ? " disabled" : " onclick=\"AdminActivityJs.go(" + (page - 1) + ")\"") + ">Previous</button><button type=\"button\" class=\"al-btn al-btn-ghost al-btn-sm\"" + (page >= pages ? " disabled" : " onclick=\"AdminActivityJs.go(" + (page + 1) + ")\"") + ">Next</button></div></div>";
        }

        private static string Outcome(string? v)
        {
            string f = (v ?? string.Empty).Trim();
            return f == "ok" || f == "refused" ? f : string.Empty;
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            List<ActivityEntry> all = await Store.Rows<ActivityEntry>("activity");
            List<Staff> staff = await Store.LoadStaff();
            bool full = Access.Can(c.U, AreaKey, 'V');
            response.SetElementContents("al-main", MainHtml(c, full, all, staff));
            response.SetElementContents("al-list", ListHtml(c, full, all, staff, Who(full, c), Outcome(GetDataValue("of")), Ui.Clip(GetDataValue("term"), 40), Ui.Int(GetDataValue("pgn"), 1, 1000, 1)));
            return response;
        }

        public async Task<ApiResponse> List()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            List<ActivityEntry> all = await Store.Rows<ActivityEntry>("activity");
            List<Staff> staff = await Store.LoadStaff();
            bool full = Access.Can(c.U, AreaKey, 'V');
            response.SetElementContents("al-list", ListHtml(c, full, all, staff, Who(full, c), Outcome(GetDataValue("of")), Ui.Clip(GetDataValue("term"), 40), Ui.Int(GetDataValue("pgn"), 1, 1000, 1)));
            return response;
        }

        private string Who(bool full, Ctx c)
        {
            return full ? (GetDataValue("who") ?? string.Empty).Trim() : c.U.Id;
        }

        private static string MainHtml(Ctx c, bool full, List<ActivityEntry> all, List<Staff> staff)
        {
            StringBuilder sb = new StringBuilder("<div class=\"al-ph\"><div><h1>" + (full ? "Activity log" : "My activity") + "</h1><p>" + (full ? "Who did what, and when: sign-ins, changes and refused requests. The newest 5,000 entries are kept." : "What you have done in the staff area, and when.") + "</p></div></div>");
            sb.Append("<div class=\"al-tools\"><div class=\"al-chips\"><button type=\"button\" class=\"al-chip al-act\" data-of=\"\" onclick=\"AdminActivityJs.outcome('')\">All</button><button type=\"button\" class=\"al-chip\" data-of=\"ok\" onclick=\"AdminActivityJs.outcome('ok')\">Done</button><button type=\"button\" class=\"al-chip\" data-of=\"refused\" onclick=\"AdminActivityJs.outcome('refused')\">Refused</button></div><div class=\"al-filters\">");
            if (full)
            {
                sb.Append("<select id=\"al-who\" aria-label=\"Person\" onchange=\"AdminActivityJs.search()\"><option value=\"\">Everyone</option>");
                if (Store.Demo())
                {
                    sb.Append("<option value=\"u-demo\">" + Ui.Esc(Store.DemoManager().Name) + "</option>");
                }
                foreach (Staff s in staff.OrderBy(x => x.Name, StringComparer.OrdinalIgnoreCase))
                {
                    sb.Append("<option value=\"" + Ui.Esc(s.Id) + "\">" + Ui.Esc(s.Name) + "</option>");
                }
                sb.Append("<option value=\"system\">System</option></select>");
            }
            sb.Append("<input type=\"search\" id=\"al-term\" placeholder=\"Search what or which\" maxlength=\"40\" oninput=\"AdminActivityJs.search()\" aria-label=\"Search the log\"></div></div><div id=\"al-list\"></div>");
            return sb.ToString();
        }

        private static string ListHtml(Ctx c, bool full, List<ActivityEntry> all, List<Staff> staff, string who, string of, string term, int page)
        {
            List<ActivityEntry> rows = all.Where(a => (who == string.Empty || a.User == who) && (of == string.Empty || (of == "ok") == a.Ok) && (term == string.Empty || Ui.Has(a.Action, term) || Ui.Has(a.Target, term))).OrderByDescending(a => a.When).ToList();
            if (rows.Count == 0)
            {
                return "<div class=\"al-panel al-empty\">" + (all.Count == 0 ? "Nothing has been logged yet." : "No entries match.") + "</div>";
            }
            int pages = Math.Max(1, (rows.Count + Size - 1) / Size);
            page = Math.Min(page, pages);
            StringBuilder sb = new StringBuilder("<div class=\"al-wrapt\"><table class=\"al-table\"><thead><tr><th>When</th>" + (full ? "<th>Who</th>" : string.Empty) + "<th>What</th><th>Which</th><th>Result</th></tr></thead><tbody>");
            foreach (ActivityEntry a in rows.Skip((page - 1) * Size).Take(Size))
            {
                sb.Append("<tr><td class=\"al-first\">" + Ui.Esc(Ui.When(a.When)) + "</td>" + (full ? "<td data-l=\"Who\">" + Ui.Esc(Store.NameOf(staff, a.User)) + "</td>" : string.Empty) + "<td data-l=\"What\">" + Ui.Esc(a.Action) + "</td><td data-l=\"Which\" class=\"al-target\">" + Ui.Esc(a.Target) + "</td><td data-l=\"Result\">" + (a.Ok ? "<span class=\"al-pill al-pill-go\">Done</span>" : "<span class=\"al-pill al-pill-no\">Refused</span>") + "</td></tr>");
            }
            sb.Append("</tbody></table></div>" + Pager(page, pages, rows.Count));
            return sb.ToString();
        }
    }
}
