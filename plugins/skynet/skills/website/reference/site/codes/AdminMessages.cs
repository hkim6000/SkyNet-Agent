using System.Text;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminMessages : WebPage
    {
        private const string AreaKey = "messages";
        private const int Size = 10;
        private static readonly (string Key, string Name, string Pill)[] States = { ("new", "New", "mx-pill-new"), ("replied", "Replied", "mx-pill-go"), ("waiting", "Waiting for them", "mx-pill-wait"), ("closed", "Closed", "mx-pill-off") };

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Messages | Staff");
            HtmlDoc.AddMetaElement("robots", "noindex, nofollow");
        }

        private async Task<Ctx?> Guard(ApiResponse response)
        {
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminMessagesJs.expired();");
            }
            return c;
        }

        private static async Task<ApiResponse> Refuse(ApiResponse response, Ctx c, string action, string target, string message)
        {
            await Store.Log(c.U.Id, action, target, false);
            response.ExecuteScript("AdminMessagesJs.toast('" + Ui.Js(message) + "');");
            return response;
        }

        private string Field(string key, int max)
        {
            return Ui.Clip((GetDataValue(key) ?? string.Empty).Replace("\r", string.Empty), max);
        }

        private static string Pager(string ns, int page, int pages, int total, string one, string many)
        {
            return "<div class=\"mx-pager\"><span>Page " + page + " of " + pages + " &middot; " + Ui.Count(total, one, many) + "</span><div><button type=\"button\" class=\"mx-btn mx-btn-ghost mx-btn-sm\"" + (page <= 1 ? " disabled" : " onclick=\"" + ns + ".go(" + (page - 1) + ")\"") + ">Previous</button><button type=\"button\" class=\"mx-btn mx-btn-ghost mx-btn-sm\"" + (page >= pages ? " disabled" : " onclick=\"" + ns + ".go(" + (page + 1) + ")\"") + ">Next</button></div></div>";
        }
        private static string State(string k)
        {
            foreach (var s in States)
            {
                if (s.Key == k)
                {
                    return "<span class=\"mx-pill " + s.Pill + "\">" + s.Name + "</span>";
                }
            }
            return "<span class=\"mx-pill\">" + Ui.Esc(k) + "</span>";
        }

        private static string Filter(string? v)
        {
            string f = (v ?? string.Empty).Trim();
            return f == "unread" || States.Any(s => s.Key == f) ? f : string.Empty;
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!Access.Can(c.U, AreaKey, 'V'))
            {
                response.SetElementContents("mx-main", "<div class=\"mx-panel\"><h1>No access</h1><p class=\"mx-hint\">You do not have access to messages. Ask a manager if you need it.</p></div>");
                return response;
            }
            List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
            string f = Filter(GetDataValue("mf"));
            string term = Ui.Clip(GetDataValue("term"), 40);
            int page = Ui.Int(GetDataValue("pgn"), 1, 1000, 1);
            response.SetElementContents("mx-main", MainHtml(all, f, term, page));
            response.ExecuteScript("AdminMessagesJs.loaded('" + f + "');");
            return response;
        }

        private static string MainHtml(List<ContactMessage> all, string f, string term, int page)
        {
            StringBuilder sb = new StringBuilder("<div class=\"mx-ph\"><div><h1>Messages</h1><p>Messages from the contact form. Opening one marks it as read.</p></div></div>");
            sb.Append("<div class=\"mx-tools\"><div class=\"mx-chips\" id=\"mx-chips\">" + Chip(string.Empty, "All", all.Count, f) + Chip("unread", "Unread", all.Count(m => !m.Read), f));
            foreach (var s in States)
            {
                sb.Append(Chip(s.Key, s.Name, all.Count(m => m.Status == s.Key), f));
            }
            sb.Append("</div><input type=\"search\" id=\"mx-term\" placeholder=\"Search name, email or reference\" maxlength=\"40\" value=\"" + Ui.Esc(term) + "\" oninput=\"AdminMessagesJs.search()\" aria-label=\"Search messages\"></div>");
            sb.Append("<div id=\"mx-list\">" + ListHtml(all, f, term, page) + "</div>");
            return sb.ToString();
        }

        private static string Chip(string key, string name, int n, string cur)
        {
            return "<button type=\"button\" class=\"mx-chip" + (key == cur ? " mx-act" : string.Empty) + "\" data-mf=\"" + key + "\" onclick=\"AdminMessagesJs.filter('" + key + "')\">" + name + " <small>" + n + "</small></button>";
        }

        public async Task<ApiResponse> List()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null || !Access.Can(c.U, AreaKey, 'V'))
            {
                return response;
            }
            List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
            response.SetElementContents("mx-list", ListHtml(all, Filter(GetDataValue("mf")), Ui.Clip(GetDataValue("term"), 40), Ui.Int(GetDataValue("pgn"), 1, 1000, 1)));
            return response;
        }

        private static string ListHtml(List<ContactMessage> all, string f, string term, int page)
        {
            List<ContactMessage> rows = all.Where(m => (f == string.Empty || (f == "unread" ? !m.Read : m.Status == f)) && (term == string.Empty || Ui.Has(m.Name, term) || Ui.Has(m.Email, term) || Ui.Has(m.Id, term) || Ui.Has(m.Phone, term))).OrderByDescending(m => m.When).ToList();
            if (rows.Count == 0)
            {
                return "<div class=\"mx-panel mx-empty\">" + (all.Count == 0 ? "No messages yet. Messages from the contact form appear here." : "No messages match.") + "</div>";
            }
            int pages = Math.Max(1, (rows.Count + Size - 1) / Size);
            page = Math.Min(page, pages);
            StringBuilder sb = new StringBuilder("<div class=\"mx-wrapt\"><table class=\"mx-table\"><thead><tr><th>From</th><th>Received</th><th>Topic</th><th>Status</th></tr></thead><tbody>");
            foreach (ContactMessage m in rows.Skip((page - 1) * Size).Take(Size))
            {
                sb.Append("<tr class=\"mx-row" + (m.Read ? string.Empty : " mx-unread") + "\" tabindex=\"0\" onclick=\"AdminMessagesJs.open('" + Ui.Js(m.Id) + "')\" onkeydown=\"if(event.key==='Enter'){AdminMessagesJs.open('" + Ui.Js(m.Id) + "')}\"><td class=\"mx-first\"><b>" + (m.Read ? string.Empty : "<i class=\"mx-dot\" aria-label=\"Unread\"></i>") + Ui.Esc(m.Name) + "</b><small>" + Ui.Esc(m.Email) + " &middot; " + Ui.Esc(m.Id) + "</small></td>");
                sb.Append("<td data-l=\"Received\">" + Ui.Esc(Ui.When(m.When)) + "</td><td data-l=\"Topic\">" + (m.Topic == string.Empty ? "None" : Ui.Esc(m.Topic)) + "</td><td data-l=\"Status\">" + State(m.Status) + "</td></tr>");
            }
            sb.Append("</tbody></table></div>" + Pager("AdminMessagesJs", page, pages, rows.Count, "message", "messages"));
            return sb.ToString();
        }

        public async Task<ApiResponse> Open()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'V'))
            {
                return await Refuse(response, c, "open message", id, "You do not have access to messages.");
            }
            ContactMessage? m = null;
            bool marked = false;
            using (await Store.Hold())
            {
                List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
                m = all.FirstOrDefault(x => x.Id == id);
                if (m != null && !m.Read)
                {
                    m.Read = true;
                    marked = true;
                    await Store.SaveRows("messages", all);
                }
            }
            if (m == null)
            {
                response.ExecuteScript("AdminMessagesJs.toast('That message was not found. It may have been deleted.');");
                return response;
            }
            response.SetElementContents("mx-mbody", DetailHtml(c, m));
            if (marked)
            {
                List<ContactMessage> fresh = await Store.Rows<ContactMessage>("messages");
                response.SetElementContents("mx-main", MainHtml(fresh, Filter(GetDataValue("mf")), Ui.Clip(GetDataValue("term"), 40), Ui.Int(GetDataValue("pgn"), 1, 1000, 1)));
            }
            response.ExecuteScript("AdminMessagesJs.opened('" + Ui.Js(m.Name + " · " + m.Id) + "'," + (marked ? "true" : "false") + ");");
            return response;
        }

        private static string DetailHtml(Ctx c, ContactMessage m)
        {
            bool canE = Access.Can(c.U, AreaKey, 'E');
            string tel = new string(m.Phone.Where(ch => char.IsDigit(ch) || ch == '+').ToArray());
            StringBuilder sb = new StringBuilder("<div class=\"mx-stack\"><dl class=\"mx-kv\"><dt>Received</dt><dd>" + Ui.Esc(Ui.When(m.When)) + "</dd><dt>Email</dt><dd><a href=\"mailto:" + Ui.Esc(m.Email) + "\">" + Ui.Esc(m.Email) + "</a></dd><dt>Phone</dt><dd>" + (m.Phone == string.Empty ? "Not given" : "<a href=\"tel:" + Ui.Esc(tel) + "\">" + Ui.Esc(m.Phone) + "</a>") + "</dd><dt>Topic</dt><dd>" + (m.Topic == string.Empty ? "None" : Ui.Esc(m.Topic)) + "</dd></dl>");
            if (m.Text != string.Empty)
            {
                sb.Append("<div class=\"mx-msg\">" + Ui.Esc(m.Text).Replace("\n", "<br>") + "</div>");
            }
            sb.Append("<form class=\"mx-stack\" id=\"mx-form\" onsubmit=\"return AdminMessagesJs.save('" + Ui.Js(m.Id) + "')\" novalidate><fieldset class=\"mx-stack mx-fs\"" + (canE ? string.Empty : " disabled") + "><label class=\"mx-field\" for=\"mx-f-status\"><span>Status</span><select id=\"mx-f-status\" data-k=\"status\">");
            foreach (var s in States)
            {
                sb.Append("<option value=\"" + s.Key + "\"" + (s.Key == m.Status ? " selected" : string.Empty) + ">" + s.Name + "</option>");
            }
            sb.Append("</select><em class=\"mx-err\" id=\"mx-e-status\"></em></label><label class=\"mx-field\" for=\"mx-f-note\"><span>Note for staff</span><textarea id=\"mx-f-note\" data-k=\"note\" rows=\"3\" maxlength=\"600\">" + Ui.Esc(m.Note) + "</textarea><small>Only what staff need to follow it up, such as when you replied.</small><em class=\"mx-err\" id=\"mx-e-note\"></em></label></fieldset>");
            sb.Append("<div class=\"mx-acts\">" + (canE ? "<button type=\"submit\" class=\"mx-btn\">Save</button><button type=\"button\" class=\"mx-btn mx-btn-ghost\" onclick=\"AdminMessagesJs.unread('" + Ui.Js(m.Id) + "')\">Mark as unread</button>" : string.Empty) + "<button type=\"button\" class=\"mx-btn mx-btn-ghost\" onclick=\"AdminMessagesJs.closeModal()\">Close</button>" + (Access.Can(c.U, AreaKey, 'X') ? "<button type=\"button\" class=\"mx-btn mx-btn-danger mx-push\" onclick=\"AdminMessagesJs.drop('" + Ui.Js(m.Id) + "','" + Ui.Js(m.Name) + "')\">Delete</button>" : string.Empty) + "</div></form></div>");
            return sb.ToString();
        }

        public async Task<ApiResponse> Save()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "save message", id, "You can read messages but not change them.");
            }
            string status = (GetDataValue("status") ?? string.Empty).Trim();
            string note = Field("note", 800).Trim();
            string eStatus = States.Any(s => s.Key == status) ? string.Empty : "Choose a status.";
            string eNote = note.Length > 600 ? "Keep the note under 600 characters." : string.Empty;
            response.SetElementContents("mx-e-status", eStatus);
            response.SetElementContents("mx-e-note", eNote);
            if (eStatus + eNote != string.Empty)
            {
                return response;
            }
            bool found = false;
            using (await Store.Hold())
            {
                List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
                ContactMessage? m = all.FirstOrDefault(x => x.Id == id);
                if (m != null)
                {
                    found = true;
                    m.Status = status;
                    m.Note = note;
                    m.Read = true;
                    m.Changed = DateTime.UtcNow;
                    await Store.SaveRows("messages", all);
                }
            }
            if (!found)
            {
                response.ExecuteScript("AdminMessagesJs.toast('That message was deleted.');");
                return response;
            }
            await Store.Log(c.U.Id, "save message", id + " · " + status, true);
            return await Relist(response, "AdminMessagesJs.saved('Saved');");
        }

        public async Task<ApiResponse> Unread()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "mark unread", id, "You can read messages but not change them.");
            }
            using (await Store.Hold())
            {
                List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
                ContactMessage? m = all.FirstOrDefault(x => x.Id == id);
                if (m != null)
                {
                    m.Read = false;
                    await Store.SaveRows("messages", all);
                }
            }
            return await Relist(response, "AdminMessagesJs.saved('Marked as unread');");
        }

        public async Task<ApiResponse> Drop()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            if (!Access.Can(c.U, AreaKey, 'X'))
            {
                return await Refuse(response, c, "delete message", id, "You are not allowed to delete messages.");
            }
            bool gone = false;
            using (await Store.Hold())
            {
                List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
                gone = all.RemoveAll(x => x.Id == id) > 0;
                if (gone)
                {
                    await Store.SaveRows("messages", all);
                }
            }
            if (gone)
            {
                await Store.Log(c.U.Id, "delete message", id, true);
            }
            return await Relist(response, "AdminMessagesJs.saved('" + (gone ? "Message deleted" : "That message was already deleted") + "');");
        }

        private async Task<ApiResponse> Relist(ApiResponse response, string script)
        {
            List<ContactMessage> all = await Store.Rows<ContactMessage>("messages");
            response.SetElementContents("mx-main", MainHtml(all, Filter(GetDataValue("mf")), Ui.Clip(GetDataValue("term"), 40), Ui.Int(GetDataValue("pgn"), 1, 1000, 1)));
            response.ExecuteScript(script);
            return response;
        }
    }
}
