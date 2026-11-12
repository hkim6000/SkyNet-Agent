using System.Text;
using System.Text.Json;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class AdminThings : WebPage
    {
        private const string AreaKey = "things";

        private const int Max = 12;

        private static string Thumb(List<MediaItem> media, string path)
        {
            MediaItem? x = media.FirstOrDefault(i => i.Path == path);
            return x != null && x.Thumb != string.Empty ? x.Thumb : path;
        }


        private static string StripItem(List<MediaItem> media, string path, bool canE)
        {
            return "<div class=\"tg-si\" data-src=\"" + Ui.Esc(path) + "\"><img src=\"" + Ui.Esc(Thumb(media, path)) + "\" alt=\"\"><i class=\"tg-sn\"></i>" + (canE ? "<div class=\"tg-sctl\"><button type=\"button\" aria-label=\"Move earlier\" onclick=\"AdminThingsJs.sMove(this,-1)\">&#9664;</button><button type=\"button\" aria-label=\"Move later\" onclick=\"AdminThingsJs.sMove(this,1)\">&#9654;</button><button type=\"button\" aria-label=\"Remove\" onclick=\"AdminThingsJs.sDrop(this)\">&#10005;</button></div>" : string.Empty) + "</div>";
        }


        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Things | Staff");
        }

        private async Task<Ctx?> Guard(ApiResponse response)
        {
            Ctx? c = await Auth.Check(GetDataValue("tok"));
            if (c == null)
            {
                response.ExecuteScript("AdminThingsJs.expired();");
            }
            return c;
        }

        private static async Task<ApiResponse> Refuse(ApiResponse response, Ctx c, string action, string target, string message)
        {
            await Store.Log(c.U.Id, action, target, false);
            response.ExecuteScript("AdminThingsJs.toast('" + Ui.Js(message) + "');");
            return response;
        }

        public async Task<ApiResponse> Load()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            List<Thing> all = await Store.Rows<Thing>("things");
            response.SetElementContents("tg-main", "<div class=\"tg-ph\"><div><h1>Things</h1></div></div><div class=\"tg-wrapt\"><table class=\"tg-table\"><tbody>" + string.Concat(all.Select(t => "<tr class=\"tg-row\" onclick=\"AdminThingsJs.open('" + Ui.Js(t.Id) + "')\"><td class=\"tg-first\"><b>" + Ui.Esc(t.Name) + "</b></td><td data-l=\"Photos\">" + t.Photos.Count + "</td></tr>")) + "</tbody></table></div>");
            return response;
        }

        public async Task<ApiResponse> Open()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            bool canE = Access.Can(c.U, AreaKey, 'E');
            List<Thing> all = await Store.Rows<Thing>("things");
            Thing? item = all.FirstOrDefault(x => x.Id == GetDataValue("id"));
            if (item == null)
            {
                return response;
            }
            List<MediaItem> media = await Media.Load();
            StringBuilder sb = new StringBuilder("<form class=\"tg-stack\" id=\"tg-form\" onsubmit=\"return AdminThingsJs.save('" + Ui.Js(item.Id) + "')\" novalidate>");
            sb.Append("<p class=\"tg-hint\">Photos from the media library, in order. The first one is the card picture. Up to " + Max + " photos.</p><div class=\"tg-strip\" id=\"tg-strip\">");
            foreach (string p in item.Photos)
            {
                sb.Append(StripItem(media, p, canE));
            }
            sb.Append("</div><em class=\"tg-err\" id=\"tg-e-photos\"></em>" + (canE ? "<div><button type=\"button\" class=\"tg-btn tg-btn-ghost\" onclick=\"AdminThingsJs.pickPhotos()\">Choose photos</button></div>" : string.Empty));
            sb.Append("<div class=\"tg-acts\"><button type=\"submit\" class=\"tg-btn\">Save</button></div></form>");
            response.SetElementContents("tg-mbody", sb.ToString());
            response.ExecuteScript("AdminThingsJs.opened('" + Ui.Js(item.Name) + "');");
            return response;
        }

        public async Task<ApiResponse> Save()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "save thing", string.Empty, "No.");
            }
            Dictionary<string, string> e = new Dictionary<string, string>();
            List<MediaItem> media = await Media.Load();
            List<string>? photos = null;
            try
            {
                photos = JsonSerializer.Deserialize<List<string>>(GetDataValue("photos") ?? "[]");
            }
            catch (JsonException)
            {
                photos = null;
            }
            photos = (photos ?? new List<string>()).Distinct().ToList();
            if (photos.Count > Max)
            {
                e["photos"] = "Choose up to " + Max + " photos.";
            }
            else if (photos.Any(p => Media.Find(media, p, "photo") == null))
            {
                e["photos"] = "A photo is no longer in the media library. Choose the photos again.";
            }

            response.SetElementContents("tg-e-photos", e.TryGetValue("photos", out string? pe) ? pe : string.Empty);
            if (e.Count > 0)
            {
                return response;
            }
            using (await Store.Hold())
            {
                List<Thing> all = await Store.Rows<Thing>("things");
                Thing? t = all.FirstOrDefault(x => x.Id == GetDataValue("id"));
                if (t != null)
                {
                    t.Photos = photos;
                    await Store.SaveRows("things", all);
                }
            }
            response.ExecuteScript("AdminThingsJs.saved('Saved');");
            return response;
        }

        private static readonly JsonSerializerOptions ReadJson = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

        private static readonly string[] Kinds = { "living", "dining", "kitchen", "bed", "bath", "office", "entry", "hall", "stairs", "closet", "laundry", "garage", "balcony" };
        private static readonly string[] OpeningKinds = { "door", "window", "open" };

        private static (FloorPlan? Plan, string Error) CleanPlan(string? raw)
        {
            FloorPlan? p;
            try
            {
                p = JsonSerializer.Deserialize<FloorPlan>((raw ?? string.Empty).Length > 200000 || string.IsNullOrWhiteSpace(raw) ? "{}" : raw, ReadJson);
            }
            catch (JsonException)
            {
                return (null, "The floor plan could not be read. Reload and try again.");
            }
            FloorPlan clean = new FloorPlan();
            foreach (PlanFloor f in (p?.Floors ?? new List<PlanFloor>()).Take(4))
            {
                PlanFloor nf = new PlanFloor { Name = Ui.Line(f.Name, 24).Trim() };
                foreach (PlanRoom r in (f.Rooms ?? new List<PlanRoom>()).Take(40))
                {
                    string name = Ui.Line(r.Name, 30).Trim();
                    nf.Rooms.Add(new PlanRoom { Name = name != string.Empty ? name : "Room", Kind = Kinds.Contains(r.Kind) ? r.Kind : "living", X = Math.Clamp(r.X, -60, 300), Y = Math.Clamp(r.Y, -60, 300), W = Math.Clamp(r.W, 2, 150), H = Math.Clamp(r.H, 2, 150) });
                }
                foreach (PlanOpening o in (f.Openings ?? new List<PlanOpening>()).Take(160))
                {
                    if (OpeningKinds.Contains(o.Kind))
                    {
                        nf.Openings.Add(new PlanOpening { Kind = o.Kind, Dir = o.Dir == "v" ? "v" : "h", X = Math.Clamp(o.X, -60, 300), Y = Math.Clamp(o.Y, -60, 300), Len = Math.Clamp(o.Len, 1, 40) });
                    }
                }
                for (int i = 0; i < nf.Rooms.Count; i++)
                {
                    for (int j = i + 1; j < nf.Rooms.Count; j++)
                    {
                        PlanRoom a = nf.Rooms[i], b = nf.Rooms[j];
                        if (a.X < b.X + b.W && b.X < a.X + a.W && a.Y < b.Y + b.H && b.Y < a.Y + a.H)
                        {
                            return (null, (nf.Name == string.Empty ? "A floor" : nf.Name) + ": " + a.Name + " and " + b.Name + " overlap. Move one of them.");
                        }
                    }
                }
                if (nf.Rooms.Count > 0)
                {
                    if (nf.Name == string.Empty)
                    {
                        nf.Name = "Floor " + (clean.Floors.Count + 1);
                    }
                    clean.Floors.Add(nf);
                }
            }
            return (clean, string.Empty);
        }

        public async Task<ApiResponse> SavePlan()
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
                return await Refuse(response, c, "save plan", id, "You can look but not change this.");
            }
            (FloorPlan? plan, string error) = CleanPlan(GetDataValue("plan"));
            if (plan == null)
            {
                response.ExecuteScript("AdminThingsJs.toast('" + Ui.Js(error) + "');");
                return response;
            }
            using (await Store.Hold())
            {
                List<Thing> all = await Store.Rows<Thing>("things");
                Thing? t = all.FirstOrDefault(x => x.Id == id);
                if (t != null)
                {
                    t.Plan = plan;
                    await Store.SaveRows("things", all);
                }
            }
            await Store.Log(c.U.Id, "save plan", id, true);
            response.ExecuteScript("AdminThingsJs.toast('Floor plan saved');");
            return response;
        }

        public async Task<ApiResponse> Pick()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!Access.Can(c.U, AreaKey, 'E'))
            {
                return await Refuse(response, c, "pick photos", string.Empty, "You can look but not change this.");
            }
            List<MediaItem> media = await Media.Load();
            response.SetElementContents("tg-pkgrid", PickGrid(media, Ui.Clip(GetDataValue("pterm"), 40)));
            response.ExecuteScript("AdminThingsJs.pkListed();");
            return response;
        }

        private static string PickGrid(List<MediaItem> media, string term)
        {
            List<MediaItem> rows = media.Where(m => m.Kind == "photo" && (term == string.Empty || Ui.Has(m.Name, term) || Ui.Has(m.Alt, term))).OrderBy(m => m.Name, StringComparer.Ordinal).Take(400).ToList();
            if (rows.Count == 0)
            {
                return "<p class=\"tg-hint\">Nothing matches. Upload a photo above, or add photos in the Media library.</p>";
            }
            return string.Concat(rows.Select(m => "<button type=\"button\" class=\"tg-pki\" data-src=\"" + Ui.Esc(m.Path) + "\" data-thumb=\"" + Ui.Esc(m.Thumb != string.Empty ? m.Thumb : m.Path) + "\" onclick=\"AdminThingsJs.pkToggle(this)\" title=\"" + Ui.Esc(m.Alt != string.Empty ? m.Alt : m.Name) + "\"><img src=\"" + Ui.Esc(m.Thumb != string.Empty ? m.Thumb : m.Path) + "\" alt=\"\" loading=\"lazy\"><i class=\"tg-pkn\"></i><span>" + Ui.Esc(m.Name) + "</span></button>"));
        }

        public async Task<ApiResponse> Upload()
        {
            ApiResponse response = new ApiResponse();
            Ctx? c = await Guard(response);
            if (c == null)
            {
                return response;
            }
            if (!Access.Can(c.U, AreaKey, 'E') || !Access.Can(c.U, "media", 'E'))
            {
                response.ExecuteScript("AdminThingsJs.pkUploaded('You cannot upload to the media library.');");
                return await Refuse(response, c, "upload media", string.Empty, "You cannot upload to the media library.");
            }
            SiteData site = await Store.LoadSite();
            List<Incoming> files = await Media.Received();
            if (files.Count == 0)
            {
                response.ExecuteScript("AdminThingsJs.pkUploaded('Choose a photo first.');");
                return response;
            }
            (int added, List<string> errors) = await Media.AddAll(files, site.MaxVideoMb, c.U.Name);
            if (added > 0)
            {
                await Store.Log(c.U.Id, "upload media", Ui.Count(added, "file", "files"), true);
            }
            List<MediaItem> media = await Media.Load();
            response.SetElementContents("tg-pkgrid", PickGrid(media, string.Empty));
            response.ExecuteScript("AdminThingsJs.pkUploaded('" + Ui.Js(((added > 0 ? Ui.Count(added, "file", "files") + " added to the library. " : string.Empty) + string.Join(" ", errors)).Trim()) + "');");
            return response;
        }
    }
}
