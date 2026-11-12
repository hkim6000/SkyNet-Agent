using System.Collections.Concurrent;
using System.Text;
using MySite.Models;

namespace MySite.Core
{
    public sealed class Ctx
    {
        public Staff U { get; init; } = new Staff();
        public string Tok { get; init; } = string.Empty;
    }

    public static class Auth
    {
        private static readonly SemaphoreSlim SessGate = new SemaphoreSlim(1, 1);
        private static readonly ConcurrentDictionary<string, List<DateTime>> Fails = new ConcurrentDictionary<string, List<DateTime>>();
        private static readonly TimeSpan Life = TimeSpan.FromHours(8);

        public static Func<Ctx, Task<Dictionary<string, int>>>? Badges { get; set; }

        private static Task<List<Session>> LoadSessions()
        {
            return Store.Read(Store.SessionFile, () => new List<Session>());
        }

        public static async Task<Ctx?> Check(string? tok)
        {
            string t = (tok ?? string.Empty).Trim();
            if (t.Length != 32)
            {
                return null;
            }
            Session? s;
            await SessGate.WaitAsync();
            try
            {
                List<Session> list = await LoadSessions();
                DateTime now = DateTime.UtcNow;
                s = list.FirstOrDefault(x => x.Token == t && x.Expires > now);
                if (s == null)
                {
                    return null;
                }
                if (s.Expires - now < Life - TimeSpan.FromMinutes(5))
                {
                    s.Expires = now + Life;
                    list.RemoveAll(x => x.Expires <= now);
                    await Store.Write(Store.SessionFile, list);
                }
            }
            finally
            {
                SessGate.Release();
            }
            if (s.User == "u-demo")
            {
                return Store.Demo() ? new Ctx { U = Store.DemoManager(), Tok = t } : null;
            }
            List<Staff> staff = await Store.LoadStaff();
            Staff? u = staff.FirstOrDefault(x => x.Id == s.User && x.Active && !x.MustChange);
            return u == null ? null : new Ctx { U = u, Tok = t };
        }

        public static async Task<string> Open(string user)
        {
            string tok = Access.NewToken();
            await SessGate.WaitAsync();
            try
            {
                List<Session> list = await LoadSessions();
                DateTime now = DateTime.UtcNow;
                list.RemoveAll(x => x.Expires <= now);
                list.Add(new Session { Token = tok, User = user, Expires = now + Life });
                await Store.Write(Store.SessionFile, list);
            }
            finally
            {
                SessGate.Release();
            }
            return tok;
        }

        public static async Task Close(string tok)
        {
            await SessGate.WaitAsync();
            try
            {
                List<Session> list = await LoadSessions();
                if (list.RemoveAll(x => x.Token == tok) > 0)
                {
                    await Store.Write(Store.SessionFile, list);
                }
            }
            finally
            {
                SessGate.Release();
            }
        }

        public static async Task CloseAll(string user, string keep)
        {
            await SessGate.WaitAsync();
            try
            {
                List<Session> list = await LoadSessions();
                if (list.RemoveAll(x => x.User == user && x.Token != keep) > 0)
                {
                    await Store.Write(Store.SessionFile, list);
                }
            }
            finally
            {
                SessGate.Release();
            }
        }

        public static bool Paused(string login)
        {
            string k = login.Trim().ToLowerInvariant();
            if (!Fails.TryGetValue(k, out List<DateTime>? list))
            {
                return false;
            }
            lock (list)
            {
                list.RemoveAll(x => x < DateTime.UtcNow.AddMinutes(-5));
                return list.Count >= 6;
            }
        }

        public static void Failed(string login)
        {
            List<DateTime> list = Fails.GetOrAdd(login.Trim().ToLowerInvariant(), _ => new List<DateTime>());
            lock (list)
            {
                list.Add(DateTime.UtcNow);
            }
        }

        public static void Passed(string login)
        {
            Fails.TryRemove(login.Trim().ToLowerInvariant(), out _);
        }

        public static bool CanOpen(Ctx c, string page)
        {
            if (page == Access.Home || page == "AdminAccount")
            {
                return true;
            }
            Area? a = Access.ByPage(page);
            if (a == null)
            {
                return false;
            }
            if (a.Key == "activity" && !Access.OneAdmin)
            {
                return true;
            }
            return Access.Can(c.U, a.Key, 'V');
        }

        public static async Task<string> Menu(string px, string page, Ctx c)
        {
            Dictionary<string, int> counts = Badges == null ? new Dictionary<string, int>() : await Badges(c);
            StringBuilder sb = new StringBuilder();
            sb.Append(Item(px, Access.Home, "Dashboard", page, 0));
            string group = string.Empty;
            foreach (Area a in Access.InUse())
            {
                if (!CanOpen(c, a.Page))
                {
                    continue;
                }
                if (a.Group != group && a.Group != string.Empty)
                {
                    sb.Append("<span class=\"" + px + "-mg\">" + Ui.Esc(a.Group) + "</span>");
                }
                group = a.Group;
                string name = a.Key == "activity" && !Access.Can(c.U, "activity", 'V') ? "My activity" : a.Name;
                sb.Append(Item(px, a.Page, name, page, counts.TryGetValue(a.Key, out int n) ? n : 0));
            }
            sb.Append(Item(px, "AdminAccount", "My account", page, 0));
            return sb.ToString();
        }

        private static string Item(string px, string target, string name, string page, int n)
        {
            string badge = n > 0 ? "<i class=\"" + px + "-badge\">" + n + "</i>" : string.Empty;
            return "<a class=\"" + px + "-mi" + (target == page ? " " + px + "-on" : string.Empty) + "\" href=\"Admin?p=" + target + "\" data-p=\"" + target + "\"" + (target == page ? " aria-current=\"page\"" : string.Empty) + "><span>" + Ui.Esc(name) + "</span>" + badge + "</a>";
        }

        public static string Who(string px, Ctx c)
        {
            string role = c.U.Id == "u-demo" ? "Demo mode" : Access.OneAdmin ? "Administrator" : c.U.Admin ? "Manager" : c.U.Title;
            return "<b>" + Ui.Esc(c.U.Name) + "</b><small>" + Ui.Esc(role) + "</small>";
        }
    }
}
