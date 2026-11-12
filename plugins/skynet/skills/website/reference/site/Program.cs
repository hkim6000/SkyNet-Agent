using Microsoft.AspNetCore.Http.Features;
using SkyNet;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpContextAccessor();
builder.Services.Configure<FormOptions>(o => o.MultipartBodyLengthLimit = 110L * 1024 * 1024);

var app = builder.Build();
MySite.Core.Local.Accessor = app.Services.GetRequiredService<IHttpContextAccessor>();
MySite.Core.Auth.Badges = async c =>
{
    List<MySite.Models.ContactMessage> list = await MySite.Core.Store.Rows<MySite.Models.ContactMessage>("messages");
    return new Dictionary<string, int> { { "messages", list.Count(m => !m.Read) } };
};
MySite.Core.Media.AlsoUsedBy = (site, path) => site.Items.Where(i => "images/items/" + i.Image + ".webp" == path).Select(i => "Print: " + i.Title).ToList();
string[] closed = { "appconfig", "data", "temp", "logs", "htmls", "codes", "bin", "obj" };
app.Use((context, next) =>
{
    string first = (context.Request.Path.Value ?? string.Empty).TrimStart('/').Split('/')[0].ToLowerInvariant();
    if (closed.Contains(first))
    {
        context.Response.StatusCode = 404;
        return context.Response.WriteAsync("Not found");
    }
    IHttpMaxRequestBodySizeFeature? limit = context.Features.Get<IHttpMaxRequestBodySizeFeature>();
    if (limit != null && !limit.IsReadOnly)
    {
        limit.MaxRequestBodySize = 110L * 1024 * 1024;
    }
    return next(context);
});
app.UseMiddleware<IHandler>();

app.UseStaticHttpCurrent();

MySite.Core.Init.OnStart().GetAwaiter().GetResult();

app.Run();
