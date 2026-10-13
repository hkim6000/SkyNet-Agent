# SkyNet Agent

A Claude Code plugin that builds websites on the **SkyNet Framework** (ASP.NET Core, .NET 10). Describe a site in one sentence; the agent plans it, waits for your "go", then writes the pages, paints original images, compiles, screenshots every page at three widths, tests every server method and hands you a project that runs with `dotnet run`.

It knows everything the SkyNet website templates were built with: the four-file page model, server-driven updates through `ApiResponse`, responsive layouts, original art in code, generic SQL Server pages and a full verification routine.

![Starter site built by the agent](docs/screenshot-starter.png)

## Contents

1. [What you get](#what-you-get)
2. [Prerequisites](#prerequisites)
3. [Install SkyNet](#install-skynet)
4. [Install the agent](#install-the-agent)
5. [Quick start](#quick-start)
6. [Commands and skills](#commands-and-skills)
7. [Database pages](#database-pages)
8. [Troubleshooting](#troubleshooting)
9. [Links](#links)
10. [License](#license)

## What you get

| Part | What it does |
|---|---|
| `skynet:builder` agent | Plans, waits for "go", builds, verifies, reports |
| `/skynet:site` | A new website from a short brief |
| `/skynet:page` | A new page in an existing SkyNet project |
| `/skynet:sql-page` | A list / add / edit / delete page over a SQL Server table |
| `/skynet:verify` | Source checks, compile, screenshots and interaction tests |
| Starter project | Three working pages (Home, Shop, Contact) with search, filters and a validated form |
| SQL helper | `Helper.cs` with `PutData`, `GetDataTable`, `GetListT<T>`, `GetOneT<T>` and a complete sample page |
| Art scripts | Python painters for ten styles, gallery banners and portraits, so every image is original |

## Prerequisites

| Tool | Needed for | Check |
|---|---|---|
| [.NET 10 SDK](https://dotnet.microsoft.com/download) | Building and running sites | `dotnet --version` (10.x) |
| [Claude Code](https://code.claude.com/docs) | Running the agent | `claude --version` |
| [Python 3.10+](https://www.python.org/downloads/) with Pillow, NumPy, SciPy | Painting images | `python3 --version` then `pip install pillow numpy scipy` |
| [Node.js 18+](https://nodejs.org/) with Playwright | Screenshots and interaction tests | `node --version` then `npm i playwright` and `npx playwright install chromium` |
| SQL Server or SQL Server Express | Database pages only | `sqlcmd -?` |
| Visual Studio or VS Code | Optional, for editing and debugging | |

On Windows use `py` instead of `python3` if that is how Python is installed.

## Install SkyNet

SkyNet is a NuGet package: [TheSkyLite.SkyNet](https://www.nuget.org/packages/TheSkyLite.SkyNet). The agent's starter project already references it, so `/skynet:site` needs nothing more. To add SkyNet to a project yourself, pick one of these.

**A. Start from the empty template**

```bash
git clone https://github.com/hkim6000/ASPNETCoreEmpty.SkyNet MySite
cd MySite
dotnet run
```

**B. Add it to a new ASP.NET Core project**

```bash
dotnet new web -n MySite
cd MySite
dotnet add package TheSkyLite.SkyNet
```

Replace `Program.cs`:

```csharp
using SkyNet;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpContextAccessor();

var app = builder.Build();
app.UseMiddleware<IHandler>();

app.UseStaticHttpCurrent();

app.Run();
```

Add the content folders to `MySite.csproj` so they are copied to the output:

```xml
<ItemGroup>
  <Content Include="appConfig\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="htmls\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="images\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="logs\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="scripts\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="styles\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="temp\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Include="data\**" Exclude="data\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  <Content Update="data\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
</ItemGroup>
```

Then create `appConfig/application.cfg` and the folders `codes`, `htmls`, `scripts`, `styles`, `images`, `data`, `logs`, `temp`. The simplest way is to copy them from [the starter](plugins/skynet/skills/website/starter/). The [SkyNet Developer Guide](https://www.theskylite.com/documents/SkyNet_Developer_Guide.html) explains every setting.

## Install the agent

Inside Claude Code:

```
/plugin marketplace add hkim6000/SkyNet-Agent
/plugin install skynet@skynet-agent
```

Or from a terminal:

```bash
claude plugin marketplace add hkim6000/SkyNet-Agent
claude plugin install skynet@skynet-agent
```

Restart Claude Code, then type `/skynet:` to see the commands.

**Update:** `claude plugin marketplace update skynet-agent` then `claude plugin update skynet@skynet-agent`, and restart Claude Code.
**Remove:** `claude plugin uninstall skynet@skynet-agent`.

## Quick start

```bash
mkdir sites && cd sites
claude
```

```
/skynet:site a neighbourhood bakery with a menu, online pre-orders and a contact form
```

1. The agent replies with a plan: brand, pages with prefixes, features, data, images and up to three questions.
2. Answer or change anything, then type **go**.
3. It builds the project, paints the images and runs the checks until they pass.
4. Run it:

```bash
cd Bakery
dotnet run
```

Open the address printed in the terminal. Ask for changes in plain words ("make the header darker", "add a gift card page"); the agent changes only what you ask.

A full walk-through from a fresh machine is in [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md).

## Commands and skills

| Command | Example |
|---|---|
| `/skynet:site <brief>` | `/skynet:site a yoga studio with a class timetable and bookings` |
| `/skynet:page <page>` | `/skynet:page FAQ page with search and categories` |
| `/skynet:sql-page <table>` | `/skynet:sql-page CUSTOMER with name, email, phone, city` |
| `/skynet:verify [folder]` | `/skynet:verify Bakery` |

Commands always plan first and wait for "go".

Skills load automatically when Claude works on SkyNet code, and the `skynet:builder` agent preloads all of them:

| Skill | Knows |
|---|---|
| `website` | Page model, project files, design rules, known pitfalls, README template, starter project |
| `sql` | `Helper.cs`, parameterized queries, the list / edit / save / delete pattern |
| `art` | Painting original artwork in Python, saved as WebP |
| `verify` | Source checks, compile, screenshots, interaction tests, offline stub |

Ask for the agent directly with "use the skynet builder agent to ...".

## Database pages

1. Set the connection in `appConfig/application.cfg` (keep placeholders in anything you publish):

```
app.sqldb.source | (local)
app.sqldb.catalog | MySite
app.sqldb.id | sa
app.sqldb.password | your-password
```

2. Run `/skynet:sql-page <TABLE and columns>`. The agent adds `codes/Helper.cs` (once per project), a table script under `database/`, a DTO and the page.
3. Run the table script in SQL Server Management Studio or `sqlcmd -S . -d MySite -i database/CUSTOMER.sql`.

Every query uses `SqlParameter`; user input is never joined into SQL text. See the [sample page](plugins/skynet/skills/sql/sample/) and [ITEM.sql](plugins/skynet/skills/sql/sample/database/ITEM.sql). If `Microsoft.Data.SqlClient` is not found, run `dotnet add package Microsoft.Data.SqlClient`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `NU1101` / package not found | Check internet access to nuget.org, then `dotnet restore` |
| `NETSDK1022` duplicate content items | Use the split `data` rule shown above (`Exclude` + `Update` for `*.json`) |
| Warning CS1998 (async method lacks await) | Expected for page methods without database calls; the verify step allows it |
| Port already in use | Change `applicationUrl` in `Properties/launchSettings.json` or run `dotnet run --urls http://localhost:5199` |
| `Executable doesn't exist` from Playwright | `npx playwright install chromium`, or set `CHROMIUM_PATH` to an installed Chromium |
| `ModuleNotFoundError: PIL` | `pip install pillow numpy scipy` |
| Page shows `{plhd_...}` text | The page's C# does not replace that placeholder; `/skynet:verify` finds it |
| Commands missing after install | Restart Claude Code; check `/plugin` shows `skynet` as enabled |

## Links

- SkyNet Developer Guide: https://www.theskylite.com/documents/SkyNet_Developer_Guide.html
- Website templates (full source, free): https://www.theskylite.com/SkyNetTemp
- Example built the same way: [Aldermoor Gallery](https://github.com/hkim6000/SkyNet-ArtGalleryWebsite-Asp.net.Core-Full-Source) ([live](https://www.theskylite.com/ArtGallery))
- NuGet: https://www.nuget.org/packages/TheSkyLite.SkyNet
- The SkyLite: https://www.theskylite.com
- YouTube: https://www.youtube.com/@hckim3948

![Aldermoor Gallery, one of the SkyNet templates](docs/showcase-artgallery.png)

## License

The files in this repository (agent, skills, starter, samples and scripts) are under **Part A (MIT)** of the [SkyLite & SkyNet Framework License](LICENSE). The SkyNet Framework itself (`SkyNet.dll` from the TheSkyLite.SkyNet package) is covered by **Part B**: proprietary, free to use, not open source.

Code the agent writes for your website is yours; the site still runs on `SkyNet.dll` under Part B.
