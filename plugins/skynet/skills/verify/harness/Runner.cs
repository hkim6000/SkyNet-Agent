using SkyNet;
using System.Text.Json;

public static class Runner
{
    public static async Task Main(string[] args)
    {
        string root = Environment.GetEnvironmentVariable("SKYNET_ROOT") ?? Directory.GetCurrentDirectory();
        string ns = Environment.GetEnvironmentVariable("SKYNET_NS") ?? Path.GetFileName(root.TrimEnd('/', '\\'));
        Directory.SetCurrentDirectory(root);
        string mode = args[0];
        string page = args[1];
        for (int i = 2; i + 1 < args.Length; i += 2)
        {
            if (mode == "get")
            {
                WebCore.Query[args[i]] = args[i + 1];
            }
            else
            {
                WebCore.Data[args[i]] = args[i + 1];
            }
        }
        Type? t = AppDomain.CurrentDomain.GetAssemblies().SelectMany(a => a.GetTypes()).FirstOrDefault(x => x.Name == page && x.Namespace == ns + ".codes" && typeof(WebPage).IsAssignableFrom(x));
        if (t == null)
        {
            Console.Error.WriteLine("page not found: " + ns + ".codes." + page);
            Environment.Exit(2);
        }
        WebPage p = (WebPage)Activator.CreateInstance(t!)!;
        p.DataPath = Path.Combine(root, "data");
        if (mode == "get")
        {
            p.HtmlDoc.HtmlBodyText = File.ReadAllText(Path.Combine(root, "htmls", page + ".html"));
            await p.OnInitialized();
            Console.WriteLine("<!--TITLE " + p.HtmlDoc.Title + "-->");
            Console.Write(p.HtmlDoc.HtmlBodyText);
        }
        else
        {
            var m = t!.GetMethod(mode);
            if (m == null)
            {
                Console.Error.WriteLine("method not found: " + page + "." + mode);
                Environment.Exit(3);
            }
            ApiResponse r = await (Task<ApiResponse>)m.Invoke(p, null)!;
            Console.Write(JsonSerializer.Serialize(r.Ops.Select(o => new { o.op, o.k, o.v })));
        }
    }
}
