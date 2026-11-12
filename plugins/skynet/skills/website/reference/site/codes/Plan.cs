using System.Text;
using System.Text.Json;
using MySite.Core;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class Plan : WebPage
    {
        private static readonly JsonSerializerOptions PlanJson = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Plan");
            List<Thing> all = await Store.Rows<Thing>("things");
            Thing m = all.First();
            StringBuilder sb = new StringBuilder();
            List<PlanFloor> pf = m.Plan.Floors.Where(f => f.Rooms.Count > 0).ToList();
            if (pf.Count > 0)
            {
                string pdata = JsonSerializer.Serialize(new FloorPlan { Floors = pf }, PlanJson);
                sb.Append("<section class=\"pl-wrap pl-sec pl-fp\" id=\"pl-fp\" data-plan=\"" + Ui.Esc(pdata) + "\"><div class=\"pl-fp-head\"><h2>Floor plan</h2><div class=\"pl-seg\" id=\"pl-fp-views\"><button type=\"button\" data-v=\"2d\" class=\"pl-on\" aria-pressed=\"true\" onclick=\"PlanJs.fpView('2d')\">2D plan</button><button type=\"button\" data-v=\"3d\" aria-pressed=\"false\" onclick=\"PlanJs.fpView('3d')\">3D view</button></div></div>");
                if (pf.Count > 1)
                {
                    sb.Append("<div class=\"pl-seg pl-fp-floors\" id=\"pl-fp-floors\">");
                    for (int i = 0; i < pf.Count; i++)
                    {
                        sb.Append("<button type=\"button\"" + (i == 0 ? " class=\"pl-on\" aria-pressed=\"true\"" : " aria-pressed=\"false\"") + " onclick=\"PlanJs.fpFloor(" + i + ")\">" + Ui.Esc(pf[i].Name != string.Empty ? pf[i].Name : "Floor " + (i + 1)) + "</button>");
                    }
                    sb.Append("</div>");
                }
                sb.Append("<div class=\"pl-fp-stage\"><div class=\"pl-fp-3d\" id=\"pl-fp-3d\" hidden><canvas id=\"pl-fp-cv\" aria-label=\"3D floor plan. Drag to turn it, tap a room to see its size.\"></canvas><div class=\"pl-fp-lbls\" id=\"pl-fp-lbls\"></div><div class=\"pl-fp-wait\" id=\"pl-fp-wait\" hidden>Loading the 3D view&hellip;</div><span class=\"pl-fp-tip\">Drag to turn &middot; tap a room</span><div class=\"pl-fp-ctl\"><button type=\"button\" aria-label=\"Zoom in\" onclick=\"PlanJs.fpZoom(1)\">+</button><button type=\"button\" aria-label=\"Zoom out\" onclick=\"PlanJs.fpZoom(-1)\">&minus;</button><button type=\"button\" aria-label=\"Reset the view\" onclick=\"PlanJs.fpReset()\"><svg viewBox=\"0 0 24 24\" width=\"18\" height=\"18\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M4.5 12a7.5 7.5 0 1 0 2.2-5.3\"/><path d=\"M4.5 4.5v4h4\"/></svg></button></div></div><div class=\"pl-fp-2d\" id=\"pl-fp-2d\"></div></div><div class=\"pl-fp-info\" id=\"pl-fp-info\" aria-live=\"polite\"></div><div class=\"pl-fp-list\" id=\"pl-fp-list\"></div><p class=\"pl-hint\"><span id=\"pl-fp-area\"></span> &middot; The layout is approximate; our architect adjusts it to your lot.</p></section>");
            }
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText.Replace("{plhd_plan}", sb.ToString());
        }
    }
}
