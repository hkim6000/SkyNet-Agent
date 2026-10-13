# README template for a finished SkyNet site

Fill every bracket with real values. Count pages, lines and images with commands, not guesses:

```bash
find codes htmls scripts styles -type f | xargs wc -l | tail -1
find images -type f | wc -l
```

---

```markdown
# [Brand] — SkyNet [Kind] Template

A responsive [kind] website template for **ASP.NET Core (.NET 10)**, built on the **SkyNet Framework**.

[![.NET 10](https://img.shields.io/badge/.NET-10-512BD4)](https://dotnet.microsoft.com/)
[![NuGet](https://img.shields.io/nuget/v/TheSkyLite.SkyNet?label=TheSkyLite.SkyNet)](https://www.nuget.org/packages/TheSkyLite.SkyNet)

**Live demo:** [url]

![Home page](docs/screenshot-home.png)

> **Fictional [business].** [Brand] and every [item], person and number on it are invented for demonstration. [Demo actions] are simulated — nothing is stored or charged.

## Features

- **[N] pages:** [list]
- **Responsive:** desktop, tablet and phone layouts
- [one bullet per main feature, with the server-side part named]
- **No front-end build:** plain HTML, CSS and vanilla JavaScript

![Desktop, tablet and phone](docs/screenshot-responsive.png)

## Getting started

Requirements: .NET 10 SDK.

    git clone [repo url]
    cd [folder]
    dotnet run

The SkyNet package (`TheSkyLite.SkyNet`) restores from NuGet. The app opens on **[startup page]**.

## Project structure

[tree of appConfig, codes, htmls, scripts, styles, data, images]

### One page = four files, one name

| File | Holds |
|---|---|
| `codes/[Page].cs` | the page class and its server methods |
| `htmls/[Page].html` | markup with `{plhd_*}` placeholders |
| `scripts/[Page].js` | one IIFE namespace, `[Page]Js` |
| `styles/[Page].css` | styles, every class prefixed (`[px]-`) |

## SkyNet in action

[one short JS $ApiRequest example and the matching C# method from this site]

| Page | Request | Response |
|---|---|---|
| [page] | `[Method]` | [what changes] |

## Customize it

- **Content:** edit `data/site.json`
- **Brand name, colors, fonts:** [where]

## License

- **This template:** MIT — free to use, modify and redistribute, including commercially.
- **SkyNet Framework** (`TheSkyLite.SkyNet` NuGet package): proprietary, free to use including commercial use; see the license included in the package.
```
