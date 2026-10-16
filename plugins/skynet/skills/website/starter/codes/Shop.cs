using System.Globalization;
using System.Text;
using System.Text.Json;
using Starter.Models;
using SkyNet;

namespace Starter.codes
{
    public class Shop : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Shop | Paperhouse Prints");
            HtmlDoc.AddMetaElement("viewport", "width=device-width, initial-scale=1");
            HtmlDoc.AddMetaElement("description", "Browse every Paperhouse print by category and price.");

            SiteData site = await LoadSite();
            string cat = Pick(QueryValue("c"), site.Categories.Select(c => c.Key));
            string sort = Pick(QueryValue("s"), Sorts);
            List<Item> list = Find(site, cat, sort);
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_chips}", Chips(site, cat))
                .Replace("{plhd_sort}", SortOptions(sort))
                .Replace("{plhd_cat}", cat)
                .Replace("{plhd_countline}", CountLine(list.Count))
                .Replace("{plhd_grid}", Cards(list));
        }

        private static readonly string[] Sorts = { "low", "high", "az" };

        public async Task<ApiResponse> Filter()
        {
            ApiResponse response = new ApiResponse();
            SiteData site = await LoadSite();
            string cat = Pick(GetDataValue("cat"), site.Categories.Select(c => c.Key));
            string sort = Pick(GetDataValue("order"), Sorts);
            List<Item> list = Find(site, cat, sort);
            response.SetElementContents("sh-chips", Chips(site, cat));
            response.SetElementContents("sh-count", CountLine(list.Count));
            response.SetElementContents("sh-grid", Cards(list));
            response.ExecuteScript("ShopJs.filtered('" + cat + "','" + sort + "');");
            return response;
        }

        private static List<Item> Find(SiteData site, string cat, string sort)
        {
            IEnumerable<Item> q = site.Items.Where(i => cat == string.Empty || i.Category == cat);
            switch (sort)
            {
                case "low":
                    return q.OrderBy(i => i.Price).ToList();
                case "high":
                    return q.OrderByDescending(i => i.Price).ToList();
                case "az":
                    return q.OrderBy(i => i.Title, StringComparer.OrdinalIgnoreCase).ToList();
                default:
                    return q.OrderByDescending(i => i.IsNew).ThenBy(i => i.Title, StringComparer.OrdinalIgnoreCase).ToList();
            }
        }

        private static string Chips(SiteData site, string cat)
        {
            StringBuilder sb = new StringBuilder("<button type=\"button\" class=\"sh-chip" + (cat == string.Empty ? " sh-act" : string.Empty) + "\" onclick=\"ShopJs.cat('')\">All</button>");
            foreach (Category c in site.Categories)
            {
                sb.Append("<button type=\"button\" class=\"sh-chip" + (c.Key == cat ? " sh-act" : string.Empty) + "\" onclick=\"ShopJs.cat('" + c.Key + "')\">" + HtmlEncode(c.Label) + "</button>");
            }
            return sb.ToString();
        }

        private static string SortOptions(string sort)
        {
            string[,] opts = { { "", "Newest" }, { "low", "Price: low to high" }, { "high", "Price: high to low" }, { "az", "Title A to Z" } };
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < opts.GetLength(0); i++)
            {
                sb.Append("<option value=\"" + opts[i, 0] + "\"" + (opts[i, 0] == sort ? " selected" : string.Empty) + ">" + opts[i, 1] + "</option>");
            }
            return sb.ToString();
        }


        public async Task<ApiResponse> Suggest()
        {
            ApiResponse response = new ApiResponse();
            string q = Clip(GetDataValue("term"));
            SiteData site = await LoadSite();
            StringBuilder sb = new StringBuilder();
            foreach (Item i in site.Items.Where(i => Has(i.Title, q) || Has(i.Category, q)).Take(6))
            {
                sb.Append("<a class=\"sh-sg\" href=\"Shop?c=" + i.Category + "\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"\"><span><b>" + HtmlEncode(i.Title) + "</b><small>" + Money(i.Price) + " &middot; " + HtmlEncode(i.Size) + "</small></span></a>");
            }
            response.SetElementContents("sh-sugg", sb.Length == 0 ? "<div class=\"sh-sg-none\">No prints match &ldquo;" + HtmlEncode(q) + "&rdquo;</div>" : sb.ToString());
            response.ExecuteScript("ShopJs.openSugg();");
            return response;
        }

        public async Task<ApiResponse> Newsletter()
        {
            ApiResponse response = new ApiResponse();
            string email = (GetDataValue("email") ?? string.Empty).Trim();
            if (!IsEmail(email))
            {
                response.SetElementContents("sh-nl-msg", "<span class=\"sh-err\">Please enter a valid email address.</span>");
                return response;
            }
            bool added = await AddRecord("subscribers", new Subscriber { Email = email, From = "shop", When = DateTime.UtcNow }, x => x.Email.Equals(email, StringComparison.OrdinalIgnoreCase));
            response.SetElementContents("sh-nl-msg", added ? "You&rsquo;re on the list: " + HtmlEncode(email) + "." : HtmlEncode(email) + " is already on the list.");
            response.ExecuteScript("ShopJs.newsletterDone();");
            return response;
        }

        private static string Cards(IEnumerable<Item> items)
        {
            StringBuilder sb = new StringBuilder();
            foreach (Item i in items)
            {
                sb.Append("<article class=\"sh-card\"><span class=\"sh-card-img\"><img src=\"images/items/" + i.Image + ".webp\" alt=\"" + HtmlEncode(i.Title) + "\" loading=\"lazy\">" + (i.IsNew ? "<i class=\"sh-new\">NEW</i>" : string.Empty) + "</span>");
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

        private static readonly SemaphoreSlim SaveGate = new SemaphoreSlim(1, 1);

        private static async Task<bool> AddRecord<T>(string name, T entry, Func<T, bool>? duplicate = null)
        {
            JsonSerializerOptions opts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true, PropertyNamingPolicy = JsonNamingPolicy.CamelCase, WriteIndented = true };
            string dir = Path.Combine(Directory.GetCurrentDirectory(), "data");
            string file = Path.Combine(dir, name + ".json");
            await SaveGate.WaitAsync();
            try
            {
                Directory.CreateDirectory(dir);
                List<T> list = File.Exists(file) ? JsonSerializer.Deserialize<List<T>>(await File.ReadAllTextAsync(file), opts) ?? new List<T>() : new List<T>();
                if (duplicate != null && list.Any(duplicate))
                {
                    return false;
                }
                list.Add(entry);
                string tmp = file + "." + Guid.NewGuid().ToString("N") + ".tmp";
                await File.WriteAllTextAsync(tmp, JsonSerializer.Serialize(list, opts));
                File.Move(tmp, file, true);
                return true;
            }
            finally
            {
                SaveGate.Release();
            }
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
