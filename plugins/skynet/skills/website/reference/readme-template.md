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

![Home page](docs/screenshot-home.png)

> **Sample content.** [Brand] and its [items], people and prices are placeholders; replace them with your own in [where]. Every form already saves for real ([what is saved and where]).

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

[Only for a site with a staff area: the next three sections.]

## Permissions

| Area | Rights | Extra right |
|---|---|---|
| [area] | View, Edit | [extra right, or blank] |
| Users, Settings | managers only | |

## First sign-in

1. Run the site on your computer and open **/AdminLogin**. The page shows the first user name (`admin`) and a password made just for this site. It is shown only on the computer the site runs on, and is also in `appConfig/initial-admin.txt`.
2. Sign in and choose your own password. The box and the file disappear.
3. Open **Users** and add an account for each person.

Forgot the first password before using it? Delete `appConfig/initial-admin.txt` and open the sign-in page again. Locked out of every manager account? Remove the managers from `data/staff.json` and open the sign-in page.

## Deploying

1. Publish with the `web.config` from the project (IIS). Give the application pool Modify on `data/`, `temp/` and `appConfig/` (and `images/uploads/`, created first, if the admin uploads files). Use HTTPS.
2. If nobody has signed in yet, read the first password from `appConfig/initial-admin.txt` on the server.
3. Check that `/data/staff.json` and `/appConfig/initial-admin.txt` answer 404 in a browser.

> **Redeploying:** publishing copies `data/` over the live files. Download the live `data/` folder first or leave it out of the publish.

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
