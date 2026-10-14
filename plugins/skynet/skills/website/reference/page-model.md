# The SkyNet page model

## One page = four files

For a page called `Menu` with the CSS prefix `mn`:

| File | Holds |
|---|---|
| `codes/Menu.cs` | `public class Menu : WebPage` with `OnInitialized()` and the server methods |
| `htmls/Menu.html` | the page markup, with `{plhd_*}` placeholders filled by the server |
| `scripts/Menu.js` | one IIFE namespace, `MenuJs` |
| `styles/Menu.css` | styles; every class and id starts with `mn-` |

- The URL is the class name: `/Menu`, `/Menu?id=7`. Class names must be unique in the project. A `.cs` file may sit in a subfolder of `codes/`; the URL does not change.
- SkyNet ships the page's own `.html`, `.css`, `.js` and `skynet.core.js` automatically. Use `HtmlDoc.AddCSSFile("x.css")` / `HtmlDoc.AddJsFile("x.js")` only for additional files.
- Pick a two-letter prefix per page (`hm` Home, `mn` Menu, `ct` Contact...). Use it on every class, id and CSS variable so pages never clash.
- Shared parts (header, footer, cards) are duplicated in every page's HTML and CSS with that page's prefix. This is deliberate: each page can be changed without touching another.

## C# skeleton

```csharp
using System.Globalization;
using System.Text;
using System.Text.Json;
using MySite.Models;
using SkyNet;

namespace MySite.codes
{
    public class Menu : WebPage
    {
        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Menu | Brand");
            HtmlDoc.AddMetaElement("viewport", "width=device-width, initial-scale=1");
            HtmlDoc.AddMetaElement("description", "One sentence about this page.");

            SiteData site = await LoadSite();
            string cat = Pick(QueryValue("c"), site.Categories.Select(c => c.Key));
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_title}", "Our menu")
                .Replace("{plhd_items}", ItemsHtml(site, cat));
        }

        public async Task<ApiResponse> Filter()
        {
            ApiResponse response = new ApiResponse();
            SiteData site = await LoadSite();
            string cat = Pick(GetDataValue("cat"), site.Categories.Select(c => c.Key));
            response.SetElementContents("mn-items", ItemsHtml(site, cat));
            response.ExecuteScript("MenuJs.filtered('" + cat + "');");
            return response;
        }
    }
}
```

- `HtmlDoc.HtmlBodyText` arrives already filled with `htmls/Menu.html`; only call `.Replace("{plhd_x}", ...)` on it.
- `QueryValue("k")` reads the URL query string on page load. `GetDataValue("k")` reads a value sent by `$ApiRequest`.
- Every value read from the user is untrusted: trim it, check it against an allowed list (`Pick`) or a range (`Bound`), and `HtmlEncode` it before it goes into HTML.
- A server method is `public async Task<ApiResponse> Name()` with no parameters. Private helpers are `private static`.
- `LoadSite()` reads `data/site.json` from `Path.Combine(Directory.GetCurrentDirectory(), "data")`. `DataPath` is a folder only while the page loads; during API requests it is a web address, so never read or write files through it.

## ApiResponse instructions

| Call | Effect in the browser |
|---|---|
| `response.SetElementContents("id", html)` | sets the element's innerHTML (or the value of an input) |
| `response.ExecuteScript("MenuJs.done();")` | runs JavaScript after the contents are applied |
| `response.SetVariableData("name", obj)` | sends an object; read it in JS with `$GetVarData('name')` |
| `response.ModalWindow("Title", "Message")` | shows SkyNet's message window |

One response can carry many instructions; they are applied together, in order. Build HTML with `StringBuilder`. When passing text into `ExecuteScript`, escape it (`JsText`) or serialize it with `JsonSerializer.Serialize` and replace `<` with `<`.

## JavaScript skeleton

```javascript
var MenuJs = (function () {

    function el(id) {
        return document.getElementById(id);
    }

    function call(method, list) {
        $ApiRequest('Menu/' + method, JSON.stringify(list || []));
    }

    function filter(cat) {
        call('Filter', [{ key: 'cat', vlu: cat }]);
    }

    function filtered(cat) {
        history.replaceState(null, '', 'Menu' + (cat ? '?c=' + cat : ''));
    }

    function reveal() {
    }

    return {
        reveal: reveal,
        filter: filter,
        filtered: filtered
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', MenuJs.reveal);
} else {
    MenuJs.reveal();
}
```

- Page scripts load in `<head>`, so start-up work goes in `reveal()`, run after the DOM is ready (the last six lines).
- Call the server only through `$ApiRequest('Page/Method', JSON.stringify([{ key, vlu }, ...]))`. Values are strings.
- Call `$WaitOn()` before a long request if you want SkyNet's wait indicator.
- Expose only what the HTML and the server call (`onclick="MenuJs.filter('drinks')"`, `ExecuteScript("MenuJs.filtered(...)")`).

## What the browser sends with every request

`skynet.core.js` sends, with every `$ApiRequest`:

1. the `{ key, vlu }` pairs you pass;
2. **every query-string parameter of the current URL**;
3. **every `input`, `select`, `textarea` and `button` on the page, keyed by element id** (file inputs send their files).

So:

- Never use a request key that is also a query-string name on that page. If the page URL has `?q=` or `?x=`, send `term` or `ex` instead.
- Element ids are prefixed (`mn-email`), so they never collide with your short keys (`email`).
- After reading files from an `<input type="file">` in JS, clear it (`input.value = ''`), or the next request uploads them again.
- Keep secrets out of hidden inputs: everything on the page is posted.

## Data flow for a typical form

1. HTML: inputs with prefixed ids, an `<em class="mn-err" id="mn-e-email">` under each field, and `<form onsubmit="return MenuJs.send()" novalidate>`.
2. JS `send()`: `call('Send', [{ key: 'email', vlu: val('mn-email') }, ...]); return false;`
3. C# `Send()`: validate every field, `SetElementContents` each error element (empty string clears it), return early on errors; otherwise build the result, `SetElementContents` a confirmation and `ExecuteScript("MenuJs.sent();")`.
4. JS `sent()`: clear the fields, show a toast.
