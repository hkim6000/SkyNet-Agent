using System.Globalization;
using System.Text;
using System.Text.Json;
using Starter.Models;
using SkyNet;

namespace Starter.codes
{
    public class Contact : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Contact | Paperhouse Prints");
            HtmlDoc.AddMetaElement("viewport", "width=device-width, initial-scale=1");
            HtmlDoc.AddMetaElement("description", "Questions about a print or an order? Send us a note.");

            SiteData site = await LoadSite();
            StringBuilder faq = new StringBuilder();
            foreach (Faq f in site.Faqs)
            {
                faq.Append("<details class=\"ct-faq\"><summary>" + HtmlEncode(f.Q) + "</summary><p>" + HtmlEncode(f.A) + "</p></details>");
            }
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText.Replace("{plhd_faq}", faq.ToString());
        }

        private static readonly string[] Topics = { "order", "print", "other" };

        public async Task<ApiResponse> Send()
        {
            ApiResponse response = new ApiResponse();
            string name = (GetDataValue("name") ?? string.Empty).Trim();
            string email = (GetDataValue("email") ?? string.Empty).Trim();
            string topic = Pick(GetDataValue("topic"), Topics);
            string msg = (GetDataValue("message") ?? string.Empty).Trim();
            string eName = name.Length < 2 || name.Length > 60 ? "Please enter your name." : string.Empty;
            string eEmail = !IsEmail(email) ? "Please enter a valid email address." : string.Empty;
            string eTopic = topic == string.Empty ? "Please choose a topic." : string.Empty;
            string eMsg = msg.Length < 10 ? "Please write at least 10 characters." : msg.Length > 1000 ? "Please keep it under 1,000 characters." : string.Empty;
            response.SetElementContents("ct-e-name", eName);
            response.SetElementContents("ct-e-email", eEmail);
            response.SetElementContents("ct-e-topic", eTopic);
            response.SetElementContents("ct-e-msg", eMsg);
            if (eName + eEmail + eTopic + eMsg != string.Empty)
            {
                response.SetElementContents("ct-sent", string.Empty);
                return response;
            }
            response.SetElementContents("ct-sent", "<b>Thank you, " + HtmlEncode(name) + ".</b> Your message passed every server check. (Demo: nothing was sent.)");
            response.ExecuteScript("ContactJs.sent();");
            return response;
        }

        public async Task<ApiResponse> Suggest()
        {
            ApiResponse response = new ApiResponse();
            string q = Clip(GetDataValue("term"));
            SiteData site = await LoadSite();
            StringBuilder sb = new StringBuilder();
            foreach (Item i in site.Items.Where(i => Has(i.Title, q) || Has(i.Category, q)).Take(6))
            {
                sb.Append("<a class=\"ct-sg\" href=\"Shop?c=" + i.Category + "\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"\"><span><b>" + HtmlEncode(i.Title) + "</b><small>" + Money(i.Price) + " &middot; " + HtmlEncode(i.Size) + "</small></span></a>");
            }
            response.SetElementContents("ct-sugg", sb.Length == 0 ? "<div class=\"ct-sg-none\">No prints match &ldquo;" + HtmlEncode(q) + "&rdquo;</div>" : sb.ToString());
            response.ExecuteScript("ContactJs.openSugg();");
            return response;
        }

        public async Task<ApiResponse> Newsletter()
        {
            ApiResponse response = new ApiResponse();
            string email = (GetDataValue("email") ?? string.Empty).Trim();
            if (!IsEmail(email))
            {
                response.SetElementContents("ct-nl-msg", "<span class=\"ct-err\">Please enter a valid email address.</span>");
                return response;
            }
            response.SetElementContents("ct-nl-msg", "You&rsquo;re on the list: " + HtmlEncode(email) + ". (Demo: nothing was stored.)");
            response.ExecuteScript("ContactJs.newsletterDone();");
            return response;
        }

        private static string Cards(IEnumerable<Item> items)
        {
            StringBuilder sb = new StringBuilder();
            foreach (Item i in items)
            {
                sb.Append("<article class=\"ct-card\"><span class=\"ct-card-img\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"" + HtmlEncode(i.Title) + "\" loading=\"lazy\">" + (i.IsNew ? "<i class=\"ct-new\">NEW</i>" : string.Empty) + "</span>");
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
