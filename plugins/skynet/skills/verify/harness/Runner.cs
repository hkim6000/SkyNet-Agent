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
        List<Type> named = typeof(Runner).Assembly.GetTypes().Where(x => x.Name == page && !x.IsNested && x.Namespace != "SkyNet").ToList();
        if (named.Count > 1)
        {
            Console.Error.WriteLine("not found : " + page + " is ambiguous, more than one class has this name: " + string.Join(", ", named.Select(x => x.FullName)));
            Environment.Exit(2);
        }
        Type? t = named.FirstOrDefault(x => typeof(WebPage).IsAssignableFrom(x));
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
            var all = t!.GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Static).Where(x => x.Name == mode).ToList();
            if (all.Count > 1)
            {
                Console.Error.WriteLine("method " + page + "." + mode + " is ambiguous: " + all.Count + " methods share the name");
                Environment.Exit(3);
            }
            var m = all.FirstOrDefault(x => x.IsPublic && !x.IsStatic && x.GetParameters().Length == 0);
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
