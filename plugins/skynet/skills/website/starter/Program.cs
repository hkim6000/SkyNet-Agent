using SkyNet;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpContextAccessor();

var app = builder.Build();
string[] closed = { "appconfig", "data", "temp", "logs", "htmls", "codes", "bin", "obj" };
app.Use((context, next) =>
{
    string first = (context.Request.Path.Value ?? string.Empty).TrimStart('/').Split('/')[0].ToLowerInvariant();
    if (closed.Contains(first))
    {
        context.Response.StatusCode = 404;
        return context.Response.WriteAsync("Not found");
    }
    return next(context);
});
app.UseMiddleware<IHandler>();

app.UseStaticHttpCurrent();

app.Run();
