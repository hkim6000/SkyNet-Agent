using System.Security.Cryptography;
using System.Text.Json;
using MySite.Models;

namespace MySite.Core
{
    public static class Store
    {
        private static readonly JsonSerializerOptions ReadOpts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        private static readonly JsonSerializerOptions WriteOpts = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase, WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
        private static readonly SemaphoreSlim Gate = new SemaphoreSlim(1, 1);
        private static readonly SemaphoreSlim LogGate = new SemaphoreSlim(1, 1);
        private static DateTime configStamp = DateTime.MinValue;
        private static Dictionary<string, string> config = new Dictionary<string, string>();
        private const string CodeLetters = "ACDEFGHJKLMNPQRTUVWXY34679";
        private const int KeepLog = 5000;

        public static string Root => Directory.GetCurrentDirectory();

        public static string DataDir => Path.Combine(Root, "data");

        public static string ConfigFile => Path.Combine(Root, "appConfig", "application.cfg");

        public static string SessionFile => Path.Combine(Root, "temp", "admin", "sessions.json");

        public static string InitialFile => Path.Combine(Root, "appConfig", "initial-admin.txt");

        public static string FileOf(string name)
        {
            return Path.Combine(DataDir, name + ".json");
        }

        public static async Task<IDisposable> Hold()
        {
            await Gate.WaitAsync();
            return new Release(Gate);
        }

        private sealed class Release : IDisposable
        {
            private SemaphoreSlim? gate;

            public Release(SemaphoreSlim g)
            {
                gate = g;
            }

            public void Dispose()
            {
                gate?.Release();
                gate = null;
            }
        }

        public static async Task<T> Read<T>(string file, Func<T> fallback)
        {
            if (!File.Exists(file))
            {
                return fallback();
            }
            try
            {
                return JsonSerializer.Deserialize<T>(await File.ReadAllTextAsync(file), ReadOpts) ?? fallback();
            }
            catch (JsonException)
            {
                return fallback();
            }
            catch (IOException)
            {
                return fallback();
            }
        }

        public static async Task Write<T>(string file, T data)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(file) ?? Root);
            string tmp = file + "." + Guid.NewGuid().ToString("N").Substring(0, 8) + ".tmp";
            await File.WriteAllTextAsync(tmp, JsonSerializer.Serialize(data, WriteOpts));
            File.Move(tmp, file, true);
        }

        public static Task<List<T>> Rows<T>(string name)
        {
            return Read(FileOf(name), () => new List<T>());
        }

        public static Task SaveRows<T>(string name, List<T> rows)
        {
            return Write(FileOf(name), rows);
        }

        public static async Task<SiteData> LoadSite()
        {
            return await Read(FileOf("site"), () => new SiteData());
        }

        public static Task SaveSite(SiteData site)
        {
            return Write(FileOf("site"), site);
        }

        public static Task<List<Staff>> LoadStaff()
        {
            return Rows<Staff>("staff");
        }

        public static Task SaveStaff(List<Staff> staff)
        {
            return SaveRows("staff", staff);
        }

        public static async Task Log(string user, string action, string target, bool ok)
        {
            await LogGate.WaitAsync();
            try
            {
                List<ActivityEntry> list = await Rows<ActivityEntry>("activity");
                list.Insert(0, new ActivityEntry { When = DateTime.UtcNow, User = user, Action = action, Target = target.Length > 200 ? target.Substring(0, 200) : target, Ok = ok });
                if (list.Count > KeepLog)
                {
                    list.RemoveRange(KeepLog, list.Count - KeepLog);
                }
                await SaveRows("activity", list);
            }
            finally
            {
                LogGate.Release();
            }
        }

        public static string ConfigValue(string key)
        {
            if (!File.Exists(ConfigFile))
            {
                return string.Empty;
            }
            DateTime stamp = File.GetLastWriteTimeUtc(ConfigFile);
            if (stamp != configStamp)
            {
                Dictionary<string, string> map = new Dictionary<string, string>(StringComparer.Ordinal);
                foreach (string raw in File.ReadLines(ConfigFile))
                {
                    string line = raw.Trim();
                    int bar = line.IndexOf('|');
                    if (line.StartsWith('*') || bar <= 0)
                    {
                        continue;
                    }
                    map[line.Substring(0, bar).Trim()] = line.Substring(bar + 1).Trim();
                }
                config = map;
                configStamp = stamp;
            }
            return config.TryGetValue(key, out string? v) ? v : string.Empty;
        }

        public static bool Demo()
        {
            return ConfigValue("app.app.runmode") == "0";
        }

        public static string NameOf(List<Staff> staff, string id)
        {
            if (id == "u-demo")
            {
                return DemoManager().Name;
            }
            if (id == "system")
            {
                return "System";
            }
            if (id == "unknown")
            {
                return "Unknown user name";
            }
            return staff.FirstOrDefault(s => s.Id == id)?.Name ?? "Former staff member";
        }

        public static Staff DemoManager()
        {
            return new Staff { Id = "u-demo", Login = "demo", Name = "Demo manager", Title = "Manager", Admin = true, Active = true };
        }

        public static async Task EnsureFirstManager()
        {
            if (Demo())
            {
                return;
            }
            using (await Hold())
            {
                List<Staff> staff = await LoadStaff();
                if (staff.Any(u => u.Admin && u.Active && !u.MustChange && u.Hash != string.Empty))
                {
                    return;
                }
                if (File.Exists(InitialFile) && staff.Any(u => u.Admin && u.Active && u.MustChange))
                {
                    return;
                }
                string pass = Access.NewPassword();
                Staff? u = staff.FirstOrDefault(x => x.Login == "admin");
                if (u == null)
                {
                    u = new Staff { Id = "u-admin", Login = "admin", Name = "Administrator", Title = "Manager" };
                    staff.Insert(0, u);
                }
                u.Admin = true;
                u.Active = true;
                u.MustChange = true;
                u.Hash = Access.HashPassword(pass);
                await SaveStaff(staff);
                Directory.CreateDirectory(Path.GetDirectoryName(InitialFile) ?? Root);
                await File.WriteAllTextAsync(InitialFile, "user: admin" + Environment.NewLine + "password: " + pass + Environment.NewLine);
            }
        }

        public static string InitialPassword()
        {
            if (!File.Exists(InitialFile))
            {
                return string.Empty;
            }
            string line = File.ReadAllLines(InitialFile).FirstOrDefault(l => l.StartsWith("password: ", StringComparison.Ordinal)) ?? string.Empty;
            return line.Length > 10 ? line.Substring(10).Trim() : string.Empty;
        }

        public static string NewCode(string prefix, IEnumerable<string> taken)
        {
            HashSet<string> used = taken.ToHashSet(StringComparer.Ordinal);
            while (true)
            {
                char[] c = new char[6];
                for (int i = 0; i < c.Length; i++)
                {
                    c[i] = CodeLetters[RandomNumberGenerator.GetInt32(CodeLetters.Length)];
                }
                string id = prefix + "-" + new string(c);
                if (!used.Contains(id))
                {
                    return id;
                }
            }
        }
    }
}
