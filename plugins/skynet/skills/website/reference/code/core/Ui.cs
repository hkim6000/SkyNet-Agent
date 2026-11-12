using System.Globalization;
using System.Net;
using System.Text.RegularExpressions;

namespace MySite.Core
{
    public static class Ui
    {
        public static readonly CultureInfo Us = CultureInfo.GetCultureInfo("en-US");

        public static string Esc(string? v)
        {
            return WebUtility.HtmlEncode(v ?? string.Empty);
        }

        public static string Js(string? v)
        {
            return (v ?? string.Empty).Replace("\\", "\\\\").Replace("'", "\\u0027").Replace("\"", "\\u0022").Replace("&", "\\u0026").Replace("<", "\\u003c").Replace(">", "\\u003e").Replace("\r", string.Empty).Replace("\n", "\\n");
        }

        public static string Clip(string? v, int max)
        {
            string s = (v ?? string.Empty).Trim();
            return s.Length > max ? s.Substring(0, max) : s;
        }

        public static string Line(string? v, int max)
        {
            return Clip(Regex.Replace(v ?? string.Empty, "\\s+", " "), max);
        }

        public static bool Has(string? text, string q)
        {
            return q.Length > 0 && (text ?? string.Empty).Contains(q, StringComparison.OrdinalIgnoreCase);
        }

        public static string Count(int n, string one, string many)
        {
            return n.ToString("#,0", Us) + " " + (n == 1 ? one : many);
        }

        public static string Money(decimal v)
        {
            return v.ToString("C0", Us);
        }

        public static string When(DateTime utc)
        {
            DateTime t = utc.Kind == DateTimeKind.Utc ? utc.ToLocalTime() : utc;
            return t.ToString("MMM d, yyyy h:mm tt", Us);
        }

        public static int Int(string? v, int min, int max, int fallback)
        {
            return int.TryParse((v ?? string.Empty).Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int n) ? Math.Max(min, Math.Min(max, n)) : fallback;
        }

        public static bool IsEmail(string v)
        {
            return v.Length >= 5 && v.Length <= 80 && Regex.IsMatch(v, "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");
        }

        public static bool IsPhone(string v)
        {
            string d = Regex.Replace(v, "[^0-9]", string.Empty);
            return d.Length >= 10 && d.Length <= 15 && Regex.IsMatch(v, "^[0-9+() .-]+$");
        }
    }
}
