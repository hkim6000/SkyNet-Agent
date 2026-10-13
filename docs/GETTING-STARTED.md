# Getting started

From a fresh computer to a running SkyNet website in about half an hour. Commands are shown for Windows (PowerShell) and macOS/Linux where they differ.

## 1. Install the tools

**.NET 10 SDK.** Download from https://dotnet.microsoft.com/download and install, then open a new terminal:

```bash
dotnet --version
```

It should print `10.` followed by a version number.

**Node.js 18 or later.** Download the LTS version from https://nodejs.org and install:

```bash
node --version
```

**Claude Code.** Follow https://code.claude.com/docs (the native installer or `npm install -g @anthropic-ai/claude-code`), then sign in:

```bash
claude --version
claude
```

Type `/exit` to leave after signing in.

**Python 3.10 or later** (for painting images). Download from https://www.python.org/downloads (on Windows tick "Add python.exe to PATH"), then:

```bash
python3 -m pip install pillow numpy scipy
```

On Windows use `py -m pip install pillow numpy scipy`.

**Playwright** (for screenshots and tests). In a folder where you keep your sites:

```bash
mkdir sites
cd sites
npm i playwright
npx playwright install chromium
```

## 2. Install the agent

```bash
claude plugin marketplace add hkim6000/SkyNet-Agent
claude plugin install skynet@skynet-agent
```

Check it is there:

```bash
claude plugin list
```

You should see `skynet@skynet-agent` enabled.

## 3. Build your first site

Start Claude Code in your `sites` folder:

```bash
claude
```

Type a brief:

```
/skynet:site a neighbourhood bakery with a menu, online pre-orders and a contact form
```

The agent answers with a plan, for example:

| Page | Prefix | Purpose |
|---|---|---|
| Home | hm | Hero, today's bakes, opening hours |
| Menu | mn | Categories, filters, search |
| Order | or | Pre-order cart with pickup time, validated on the server |
| Contact | ct | Address, hours and a validated message form |

Change anything you like ("add a Catering page", "use a dark green accent"). When the plan looks right, type:

```
go
```

The agent now:

1. copies the starter project and renames it,
2. writes the content file, models and each page (C#, HTML, CSS, JavaScript),
3. paints the images,
4. compiles, screenshots every page at desktop, tablet and phone widths, and clicks through every feature,
5. fixes anything that fails and reports a short table of results.

Claude Code asks for permission before running commands and writing files; approve them, or allow them for the session.

## 4. Run it

```bash
cd Bakery
dotnet run
```

The browser opens at `http://localhost:5180` (each project gets its own port; the terminal prints it). Press `Ctrl+C` to stop.

You can also open the `.csproj` in Visual Studio and press F5.

## 5. Change it

Stay in Claude Code and ask in plain words:

```
make the hero headline shorter and the buttons rounder
add an FAQ page linked from the footer
the order total should include a 5% service charge
```

Or use a command:

```
/skynet:page Gift cards page with three amounts and a demo checkout
/skynet:verify Bakery
```

The agent changes only what you ask for and re-runs the checks.

## 6. Add a database (optional)

1. Install SQL Server Express and create a database, for example `Bakery`.
2. In `appConfig/application.cfg` set:

```
app.sqldb.source | (local)
app.sqldb.catalog | Bakery
app.sqldb.id | sa
app.sqldb.password | your-password
```

3. In Claude Code:

```
/skynet:sql-page PRODUCT with name, category, price, stock, active
```

4. After "go" and the build, run the script it wrote:

```bash
sqlcmd -S . -d Bakery -i database/PRODUCT.sql
```

5. `dotnet run` and open `/Product` (or the page name the agent chose).

Never commit a real password; keep `your-password` in anything you push to GitHub.

## 7. Publish

```bash
dotnet publish -c Release -o publish
```

Copy the `publish` folder to your server (IIS, Azure App Service or any host that runs ASP.NET Core 10). The SkyNet Developer Guide covers hosting: https://www.theskylite.com/documents/SkyNet_Developer_Guide.html

## If something goes wrong

See [Troubleshooting](../README.md#troubleshooting) in the README.
