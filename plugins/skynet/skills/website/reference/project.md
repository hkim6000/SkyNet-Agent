# SkyNet project files

## Folder layout

```
MySite/
├── appConfig/application.cfg      settings (startup page, folders, placeholder secrets)
├── codes/                         page classes (C#); subfolders allowed
│   └── Models/MySiteModel.cs      DTOs shared by pages
├── htmls/                         page markup
├── scripts/                       page JavaScript
├── styles/                        page CSS
├── data/site.json                 content for sites without a database
├── images/                        WebP images, logo.svg
├── logs/  temp/  bin/             empty folders used at run time
├── Properties/launchSettings.json
├── Program.cs
└── MySite.csproj
```

The [starter](../starter/) folder contains all of these, ready to copy.

## MySite.csproj

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>MySite</RootNamespace>
    <SatelliteResourceLanguages>es</SatelliteResourceLanguages>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="TheSkyLite.SkyNet" Version="1.0.8" />
    <PackageReference Include="System.Security.Cryptography.Pkcs" Version="10.0.13" />
  </ItemGroup>

  <ItemGroup>
    <Content Include="appConfig\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="htmls\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="images\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="logs\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="scripts\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="styles\**"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="temp\**" Exclude="temp\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Update="temp\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Include="data\**" Exclude="data\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
    <Content Update="data\**\*.json"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory><CopyToPublishDirectory>Always</CopyToPublishDirectory></Content>
  </ItemGroup>

</Project>
```

Use the latest `TheSkyLite.SkyNet` version from NuGet (`dotnet add package TheSkyLite.SkyNet` updates it). The `data` and `temp` rules are split on purpose: the Web SDK already includes `*.json` as content, and including it twice fails with NETSDK1022. `temp` needs it too, because the staff sign-in writes `temp/admin/sessions.json`, so the error only appears after the first sign-in. Keep the two package lines as they are: `TheSkyLite.SkyNet` at the version in the starter and `System.Security.Cryptography.Pkcs` pinned to 10.0.13, which lifts the 9.0.x version the framework package would otherwise pull in. Add no other `System.*` packages to silence an audit warning.

## Program.cs

```csharp
using SkyNet;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpContextAccessor();

var app = builder.Build();
app.UseMiddleware<IHandler>();

app.UseStaticHttpCurrent();

app.Run();
```

## appConfig/application.cfg

The file starts with a comment header (`*****` lines). Line 2 of that header documents the run mode: `***** 2. app.app.runmode : 0.Demo (staff sign-in is filled in and any user name and password signs in), 1.Production (staff sign in with their own accounts)`. See [admin.md](admin.md#run-mode-demo-and-production).

```
app.app.name | MySite
app.app.version | 1.0
app.app.releasedate | 1/1/2026       (set to the day you deliver the site, M/D/YYYY)
app.app.runmode | 0
app.app.startup | Home
app.Settings.encryptkey | your-encrypt-key
app.folders.code | codes
app.folders.html | htmls
app.folders.script | scripts
app.folders.style | styles
app.folders.image | images
app.folders.temp | temp
app.folders.data | data
app.folders.log | logs
app.folders.bin | bin
app.sqldb.source | (local)
app.sqldb.catalog | MySite
app.sqldb.id | sa
app.sqldb.password | your-password
```

The full file in the starter has every key SkyNet reads. `app.app.startup` is the page that opens at `/`. Secrets stay as placeholders in anything you publish.

## Properties/launchSettings.json

Give each project its own ports and turn hot reload off:

```json
{
  "profiles": {
    "http": {
      "commandName": "Project",
      "launchBrowser": true,
      "applicationUrl": "http://localhost:5180",
      "environmentVariables": { "ASPNETCORE_ENVIRONMENT": "Development" },
      "hotReloadEnabled": false
    }
  }
}
```

## data/site.json pattern (sites without a database)

- One JSON file holds all content: brand facts, lists of items, people, FAQs, plans.
- One model file (`codes/Models/MySiteModel.cs`) mirrors it with plain classes; property names match the JSON keys (case-insensitive deserialization).
- Every page has its own `LoadSite()` that reads and deserializes the file.
- Things that should always look current (dates, "new" badges, schedules) are stored as day offsets and computed from `DateTime.Today`.
- Records with a deadline (a seat held for payment at the desk, an offer to pay within 24 hours) are checked on every load: expired ones are closed and the place goes to the next person in line. Sample records of that kind store their deadline as an offset from now, or they have expired before anyone sees them.
- Actions that matter (messages, newsletter sign-ups, orders, bookings, accounts) are validated and saved on the server in their own file, for example `data/messages.json`, under one lock, through a temp file and `File.Move`. Only per-visitor conveniences that need no server (a cart before checkout, favourites) live in `localStorage`.
- Files the site writes at run time (`data/messages.json`, `data/staff.json`, orders) are not part of the project: keep them out of git, and download the live `data/` folder before you publish so the live files are not overwritten.

## Publishing to IIS

Put a `web.config` next to the `.csproj` (it is published with the site). Change `MySite.dll` to the project's assembly name. Keep it this plain: it is tested on a live IIS server, and extra headers or `removeServerHeader` can stop the site from starting on some IIS versions. A published site has no `codes/` folder (the C# is compiled into the `.dll`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <location path="." inheritInChildApplications="false">
    <system.webServer>
      <handlers>
        <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
      </handlers>
      <aspNetCore processPath="dotnet" arguments=".\MySite.dll" stdoutLogEnabled="false" stdoutLogFile=".\logs\stdout" hostingModel="inprocess" />
      <directoryBrowse enabled="false" />
      <security>
        <requestFiltering>
          <requestLimits maxAllowedContentLength="31457280" />
          <hiddenSegments>
            <add segment="appConfig" />
            <add segment="htmls" />
            <add segment="data" />
            <add segment="logs" />
          </hiddenSegments>
          <fileExtensions allowUnlisted="true">
            <add fileExtension=".json" allowed="false" />
            <add fileExtension=".dll" allowed="false" />
            <add fileExtension=".exe" allowed="false" />
            <add fileExtension=".pdb" allowed="false" />
            <add fileExtension=".cfg" allowed="false" />
          </fileExtensions>
        </requestFiltering>
      </security>
    </system.webServer>
  </location>
</configuration>
```

Give the application pool identity (`IIS AppPool\<pool name>`) **Modify** on the folders the site writes, and nothing more:

| Folder | Why |
|---|---|
| `data\` | content and records the site saves |
| `temp\` | sign-in sessions, uploads in progress |
| `appConfig\` | only for a site with a staff area: the first password file (`admin.md`) |
| `images\uploads\` | only when the admin uploads files; it is not published, so create it on the server before granting |
| `logs\` | only when `stdoutLogEnabled` is turned on |

```bat
icacls data /grant "IIS AppPool\MySite":(OI)(CI)M
icacls temp /grant "IIS AppPool\MySite":(OI)(CI)M
```

After publishing, `/data/staff.json` and `/appConfig/application.cfg` must answer 404.

## When the site needs a database

Use the `sql` skill: `codes/Helper.cs` (generic Get and Put), parameterized SQL only, and the `app.sqldb.*` keys above.
