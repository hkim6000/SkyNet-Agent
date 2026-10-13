# SkyNet Agent

Build complete websites on the **SkyNet Framework** (ASP.NET Core, .NET 10) by describing them in one sentence. The agent plans the site, waits for your "go", then writes every page, paints original images, checks the layout on desktop, tablet and phone, and hands you a project that runs in Visual Studio.

![A site built by the agent](docs/screenshot-starter.png)

This guide is for Windows. You need **Visual Studio** and a paid **Claude plan (Pro or Max)**; the free plan does not include Claude Code.

---

## Part 1 - Prerequisites (one time only)

Open **PowerShell** (Start menu, type `PowerShell`). Run only the lines for the tools you don't have yet.

### 1. Install the tools

```powershell
winget install Microsoft.DotNet.SDK.10
```
.NET 10 SDK - builds and runs the websites.

```powershell
winget install Git.Git
```
Git - Claude Code uses it to run commands.

```powershell
winget install Python.Python.3.12
```
Python - the agent paints the website images with it.

```powershell
winget install OpenJS.NodeJS.LTS
```
Node.js - the agent uses it to screenshot and test your pages.

```powershell
irm https://claude.ai/install.ps1 | iex
```
Claude Code - the AI that runs the agent.

**Now close PowerShell and open a new one**, so it can find the new tools.

```powershell
py -m pip install pillow numpy scipy
```
Image libraries for Python.

### 2. Create a folder for your website projects

```powershell
mkdir C:\WebSites
```
Creates the folder.

```powershell
cd C:\WebSites
```
Moves into it.

```powershell
npm i playwright
```
Installs the page-testing tool into this folder.

```powershell
npx playwright install chromium
```
Downloads the hidden browser the tests use (about 150 MB).

### 3. Sign in to Claude Code

```powershell
claude
```
Starts Claude Code.

```
/login
```
Choose **Claude account with subscription** and sign in in the browser. Then type `/exit` to return to PowerShell.

### 4. Install the SkyNet Agent

```powershell
claude plugin marketplace add hkim6000/SkyNet-Agent
```
Adds this repository as a source of plugins.

> Downloaded the ZIP instead? Unzip it to `C:\SkyNet-Agent` and run `claude plugin marketplace add C:\SkyNet-Agent`. Use the folder that contains `.claude-plugin` and `plugins`.

```powershell
claude plugin install skynet@skynet-agent
```
Installs the agent.

### 5. Checkpoint

```powershell
claude plugin list
```
You should see:

```
Installed plugins:

  > skynet@skynet-agent
    Version: 1.0.0
    Scope: user
    Status: √ enabled
```

Prerequisites are done. You never need to repeat Part 1.

---

## Part 2 - Building a website

### 1. Create an empty project in Visual Studio

**File → New → Project → ASP.NET Core Empty**

- Project name: `Bakery`
- Location: `C:\WebSites`
- Tick **Place solution and project in the same directory**
- Framework: **.NET 10**

### 2. Open a terminal inside Visual Studio

**Tools → Command Line → Developer PowerShell**

### 3. Start Claude Code in the project folder

```powershell
cd C:\WebSites\Bakery
```
Moves into your project.

```powershell
claude
```
Starts Claude Code.

### 4. Describe your website

```
/skynet:site a bakery website with online orders. Build it in this existing project in the current folder; do not create a new folder.
```

Tip: type `/skynet` and pick **skynet:site** from the list that pops up, then type your description. Describe anything: a yoga studio, a dentist, a car wash, a photo portfolio.

### 5. Review the plan and say go

The agent replies with a plan: brand name, colours, pages, features and images. Ask for changes in plain words ("add a catering page", "use dark green"), then type:

```
go
```

When it asks permission to run commands or write files, choose **Yes**. Building takes about 10-20 minutes.

### 6. Run it

When the agent says it is done, go back to Visual Studio. If it asks to reload the project, choose **Reload All**. Press **F5**.

Your website opens in the browser.

---

## Changing your website

Stay in Claude Code and ask in plain words:

```
make the header darker
add an FAQ page linked from the footer
the order total should include a 5% service charge
```

The agent changes only what you ask, checks it again, and tells you when to press F5.

## Commands

| Command | What it does |
|---|---|
| `/skynet:site <description>` | Build a new website |
| `/skynet:page <description>` | Add one page to your website |
| `/skynet:sql-page <table and columns>` | Add a page that lists, adds, edits and deletes rows in a SQL Server table |
| `/skynet:verify` | Check the whole site again (build, layout, buttons and forms) |

Every command shows a plan first and waits for **go**.

## Common problems

| Problem | Fix |
|---|---|
| `git`, `claude` or `dotnet` "is not recognized" | Close PowerShell (or Visual Studio) and open it again |
| `running scripts is disabled` when using npm | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again |
| Claude Code says **Not logged in** or **API Usage Billing** | Type `/login` and choose your subscription account |
| `Unknown command: /skynet:` | There is a space after `skynet:`. Type `/skynet` and pick from the list |
| `/skynet` shows nothing | Run `claude plugin list` in PowerShell; if `skynet` is missing, repeat Part 1 step 4 |

## Links

- SkyNet Developer Guide: https://www.theskylite.com/documents/SkyNet_Developer_Guide.html
- Website templates (free, full source): https://www.theskylite.com/SkyNetTemp
- SkyNet on NuGet: https://www.nuget.org/packages/TheSkyLite.SkyNet
- YouTube: https://www.youtube.com/@hckim3948

![Aldermoor Gallery, one of the SkyNet templates](docs/showcase-artgallery.png)

## License

The files in this repository are under **Part A (MIT)** of the [SkyLite & SkyNet Framework License](LICENSE). The SkyNet Framework itself (`SkyNet.dll` in the TheSkyLite.SkyNet package) is covered by **Part B**: proprietary, free to use, not open source.
