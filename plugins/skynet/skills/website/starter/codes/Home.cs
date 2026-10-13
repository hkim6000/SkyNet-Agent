using System.Globalization;
using System.Text;
using System.Text.Json;
using Starter.Models;
using SkyNet;

namespace Starter.codes
{
    public class Home : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Paperhouse Prints | Small-batch art prints");
            HtmlDoc.AddMetaElement("viewport", "width=device-width, initial-scale=1");
            HtmlDoc.AddMetaElement("description", "Small-batch art prints, printed by hand.");

            SiteData site = await LoadSite();
            StringBuilder cats = new StringBuilder();
            foreach (Category c in site.Categories)
            {
                cats.Append("<a class=\"hm-cat\" href=\"Shop?c=" + c.Key + "\"><b>" + HtmlEncode(c.Label) + "</b><small>" + CountLine(site.Items.Count(i => i.Category == c.Key)) + "</small></a>");
            }
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_tagline}", HtmlEncode(site.Tagline))
                .Replace("{plhd_count}", site.Items.Count + " prints in stock")
                .Replace("{plhd_new}", Cards(site.Items.Where(i => i.IsNew).Take(4)))
                .Replace("{plhd_cats}", cats.ToString());
        }

        public async Task<ApiResponse> Suggest()
        {
            ApiResponse response = new ApiResponse();
            string q = Clip(GetDataValue("term"));
            SiteData site = await LoadSite();
            StringBuilder sb = new StringBuilder();
            foreach (Item i in site.Items.Where(i => Has(i.Title, q) || Has(i.Category, q)).Take(6))
            {
                sb.Append("<a class=\"hm-sg\" href=\"Shop?c=" + i.Category + "\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"\"><span><b>" + HtmlEncode(i.Title) + "</b><small>" + Money(i.Price) + " &middot; " + HtmlEncode(i.Size) + "</small></span></a>");
            }
            response.SetElementContents("hm-sugg", sb.Length == 0 ? "<div class=\"hm-sg-none\">No prints match &ldquo;" + HtmlEncode(q) + "&rdquo;</div>" : sb.ToString());
            response.ExecuteScript("HomeJs.openSugg();");
            return response;
        }

        public async Task<ApiResponse> Newsletter()
        {
            ApiResponse response = new ApiResponse();
            string email = (GetDataValue("email") ?? string.Empty).Trim();
            if (!IsEmail(email))
            {
                response.SetElementContents("hm-nl-msg", "<span class=\"hm-err\">Please enter a valid email address.</span>");
                return response;
            }
            response.SetElementContents("hm-nl-msg", "You&rsquo;re on the list: " + HtmlEncode(email) + ". (Demo: nothing was stored.)");
            response.ExecuteScript("HomeJs.newsletterDone();");
            return response;
        }

        private static string Cards(IEnumerable<Item> items)
        {
            StringBuilder sb = new StringBuilder();
            foreach (Item i in items)
            {
                sb.Append("<article class=\"hm-card\"><span class=\"hm-card-img\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"" + HtmlEncode(i.Title) + "\" loading=\"lazy\">" + (i.IsNew ? "<i class=\"hm-new\">NEW</i>" : string.Empty) + "</span>");
                sb.Append("<b>" + HtmlEncode(i.Title) + "</b><small>" + HtmlEncode(i.Size) + " &middot; edition of 50</small><em>" + Money(i.Price) + "</em></article>");
            }
            return sb.Length == 0 ? "<p>No prints to show.</p>" : sb.ToString();
        }

        private static string CountLine(int n)
        {
            return n == 1 ? "1 print" : n + " prints";
        }

        private static string Money(decimal v)
        {
            return "$" + v.ToString("#,0.##", CultureInfo.InvariantCulture);
        }

        private async Task<SiteData> LoadSite()
        {
            string file = Path.Combine(DataPath ?? string.Empty, "site.json");
            if (!File.Exists(file))
            {
                file = Path.Combine(Directory.GetCurrentDirectory(), "data", "site.json");
            }
            if (!File.Exists(file))
            {
                return new SiteData();
            }
            string json = await File.ReadAllTextAsync(file);
            return JsonSerializer.Deserialize<SiteData>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new SiteData();
        }

        private static string Clip(string? value)
        {
            string q = (value ?? string.Empty).Trim();
            return q.Length > 40 ? q.Substring(0, 40) : q;
        }

        private static string Pick(string? value, IEnumerable<string> allowed)
        {
            string v = (value ?? string.Empty).Trim().ToLowerInvariant();
            return allowed.Contains(v) ? v : string.Empty;
        }

        private static bool Has(string text, string q)
        {
            return q.Length > 0 && (text ?? string.Empty).Contains(q, StringComparison.OrdinalIgnoreCase);
        }

        private static bool IsEmail(string v)
        {
            if (v.Length < 5 || v.Length > 80 || v.Contains(' '))
            {
                return false;
            }
            int at = v.IndexOf('@');
            int dot = v.LastIndexOf('.');
            return at > 0 && at == v.LastIndexOf('@') && dot > at + 1 && dot < v.Length - 1;
        }
    }
}
