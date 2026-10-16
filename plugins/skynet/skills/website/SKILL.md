---
name: website
description: Knowledge base for building websites on the SkyNet Framework (ASP.NET Core .NET 10, NuGet TheSkyLite.SkyNet) - the page model, project files, design rules and known pitfalls. Use whenever you write, review or fix a SkyNet page (.cs/.html/.js/.css), a SkyNet project, or a website template built with SkyNet.
user-invocable: false
---

# SkyNet website builder

SkyNet is a server-driven web framework for ASP.NET Core. The browser calls a C# method with `$ApiRequest('Page/Method', ...)`; the method returns an `ApiResponse` that changes only the parts of the page that need to change. There is no SPA framework and no front-end build: pages are plain HTML, CSS and vanilla JavaScript, and only the C# is compiled.

## Read before you write code

| File | Read it when |
|---|---|
| [reference/page-model.md](reference/page-model.md) | Always. The four-file page, C# and JS skeletons, request and response rules |
| [reference/pitfalls.md](reference/pitfalls.md) | Always, before writing and again before verifying |
| [reference/project.md](reference/project.md) | Creating a project: folders, csproj, Program.cs, application.cfg, data/site.json |
| [reference/design.md](reference/design.md) | Designing pages: layout, responsive breakpoints, confirm dialogs, admin lists, content rules |
| [reference/admin.md](reference/admin.md) | The site has a staff area: sign-in, rights by area, activity log, the first admin password |
| [reference/readme-template.md](reference/readme-template.md) | Writing the README for a finished site |
| [starter/](starter/) | A working three-page SkyNet project to copy and extend |

For database pages, use the `sql` skill. For artwork painted in code, use the `art` skill. To check your work, use the `verify` skill.

## Working rules

1. **Review first.** Present a short plan (brand, pages, features, data, open questions) and wait for the user to say "go" before writing files.
2. **One page = four files, one name.** `codes/X.cs`, `htmls/X.html`, `scripts/X.js`, `styles/X.css`. Every page is self-contained: its own CSS prefix, its own JS namespace, its own C# methods. Duplicate small helpers per page instead of sharing them; the only shared C# is a model (DTO) file, for database work `codes/Helper.cs`, and for a staff area the sign-in, rights and storage classes in `codes/Core/` (see admin.md).
3. **Server decides, browser displays.** Validation, prices, totals, permissions and anything that matters is computed in C#. JavaScript collects input, calls the server and applies small UI states.
4. **No comments in source files.** Code must read clearly without them.
5. **Never use `await Task.CompletedTask;`.** Keep `public async Task<ApiResponse> Name()` without it; the CS1998 warning is acceptable.
6. **Ready for real use, with invented sample content.** Every form saves for real; there is no demo mode. Sample brand, products and team are invented for the owner to replace. No real trademarks, no real people, no invented reviews or testimonials.
7. **Configuration placeholders only.** `application.cfg` keeps `your-password` and `your-encrypt-key`; never write real credentials.
8. **Verify before delivering.** Compile with 0 errors, then check every page at 1440, 820 and 390 pixels wide and test every interaction (see the `verify` skill).

## Build order for a new site

1. Agree on the plan (brand, palette, fonts, pages and their prefixes, data, server methods).
2. Copy [starter/](starter/) to the new project folder and rename the namespace and project.
3. Write `data/site.json` and the model classes.
4. Build pages one at a time: HTML, then CSS, then C# (`OnInitialized` plus methods), then JS.
5. Add images (the `art` skill paints them in code; WebP, lazy loaded).
6. For a staff area, build `codes/Core/`, `AdminLogin` and the dashboard first, then one admin page per area ([reference/admin.md](reference/admin.md)).
7. Verify, fix, verify again.
8. Write the README from [reference/readme-template.md](reference/readme-template.md) with real counts.
