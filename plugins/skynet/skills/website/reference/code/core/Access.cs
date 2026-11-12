using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using MySite.Models;

namespace MySite.Core
{
    public sealed class Area
    {
        public string Key { get; init; } = string.Empty;
        public string Name { get; init; } = string.Empty;
        public string Page { get; init; } = string.Empty;
        public string Group { get; init; } = string.Empty;
        public string Extra { get; init; } = string.Empty;
        public bool AdminOnly { get; init; }
        public bool NoEdit { get; init; }
        public bool StaffOnly { get; init; }
    }

    public static class Access
    {
        public static readonly bool OneAdmin = false;

        public const string Home = "AdminHome";

        public static readonly Area[] Areas =
        {
            new Area { Key = "messages", Name = "Messages", Page = "AdminMessages", Group = "Customers", Extra = "Delete messages" },
            new Area { Key = "media", Name = "Media library", Page = "AdminMedia", Group = "Website", Extra = "Delete files" },
            new Area { Key = "pages", Name = "Pages", Page = "AdminPages", Group = "Website" },
            new Area { Key = "activity", Name = "Activity log", Page = "AdminActivity", Group = "Account", NoEdit = true, StaffOnly = true },
            new Area { Key = "settings", Name = "Settings", Page = "AdminSettings", Group = "Account", AdminOnly = true },
            new Area { Key = "users", Name = "Users", Page = "AdminUsers", Group = "Account", AdminOnly = true, StaffOnly = true }
        };

        private const string Letters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
        private const int Rounds = 100000;

        public static IEnumerable<Area> InUse()
        {
            return Areas.Where(a => !OneAdmin || !a.StaffOnly);
        }

        public static Area? ByPage(string page)
        {
            return InUse().FirstOrDefault(a => a.Page == page);
        }

        public static string Level(Staff u, string area)
        {
            if (!u.Active)
            {
                return string.Empty;
            }
            Area? a = InUse().FirstOrDefault(x => x.Key == area);
            if (a == null)
            {
                return string.Empty;
            }
            if (OneAdmin || u.Admin)
            {
                return a.NoEdit ? "V" : "VE" + (a.Extra.Length > 0 ? "X" : string.Empty);
            }
            if (a.AdminOnly)
            {
                return string.Empty;
            }
            return u.Perms.TryGetValue(area, out string? p) ? Clean(a, p) : string.Empty;
        }

        public static bool Can(Staff u, string area, char right)
        {
            return Level(u, area).Contains(right);
        }

        public static string Clean(Area a, string? letters)
        {
            string p = (letters ?? string.Empty).ToUpperInvariant();
            bool v = p.Contains('V') || p.Contains('E');
            bool e = !a.NoEdit && p.Contains('E');
            bool x = e && a.Extra.Length > 0 && p.Contains('X');
            return (v ? "V" : string.Empty) + (e ? "E" : string.Empty) + (x ? "X" : string.Empty);
        }

        public static Dictionary<string, string> CleanGrid(Dictionary<string, string>? grid)
        {
            Dictionary<string, string> res = new Dictionary<string, string>();
            foreach (Area a in InUse().Where(x => !x.AdminOnly))
            {
                string p = grid != null && grid.TryGetValue(a.Key, out string? v) ? Clean(a, v) : string.Empty;
                if (p.Length > 0)
                {
                    res[a.Key] = p;
                }
            }
            return res;
        }

        public static string Words(Staff u)
        {
            if (u.Admin)
            {
                return "Manager: every area";
            }
            List<string> parts = new List<string>();
            foreach (Area a in InUse().Where(x => !x.AdminOnly))
            {
                string p = Level(u, a.Key);
                if (p.Length == 0)
                {
                    continue;
                }
                string w = p.Contains('E') ? "edit" : "view";
                if (p.Contains('X'))
                {
                    w += ", " + a.Extra.ToLowerInvariant();
                }
                parts.Add(a.Name + ": " + w);
            }
            return parts.Count == 0 ? "No areas" : string.Join(" · ", parts);
        }

        public static string HashPassword(string password)
        {
            byte[] salt = RandomNumberGenerator.GetBytes(16);
            byte[] hash = Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(password), salt, Rounds, HashAlgorithmName.SHA256, 32);
            return "pbkdf2$" + Rounds.ToString(CultureInfo.InvariantCulture) + "$" + Convert.ToBase64String(salt) + "$" + Convert.ToBase64String(hash);
        }

        public static bool VerifyPassword(string password, string stored)
        {
            string[] p = (stored ?? string.Empty).Split('$');
            if (p.Length != 4 || p[0] != "pbkdf2" || !int.TryParse(p[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int rounds) || rounds < 1000)
            {
                return false;
            }
            try
            {
                byte[] salt = Convert.FromBase64String(p[2]);
                byte[] want = Convert.FromBase64String(p[3]);
                byte[] got = Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(password ?? string.Empty), salt, rounds, HashAlgorithmName.SHA256, want.Length);
                return CryptographicOperations.FixedTimeEquals(got, want);
            }
            catch (FormatException)
            {
                return false;
            }
        }

        public static string NewPassword()
        {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 12; i++)
            {
                if (i > 0 && i % 4 == 0)
                {
                    sb.Append('-');
                }
                sb.Append(Letters[RandomNumberGenerator.GetInt32(Letters.Length)]);
            }
            return sb.ToString();
        }

        public static string NewToken()
        {
            return Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
        }
    }
}
