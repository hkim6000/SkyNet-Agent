---
name: site
description: Start a new SkyNet website from a short brief - plan the brand, pages and features, wait for "go", then build the full project from the starter, paint the images, verify it and write the README.
argument-hint: "<what the site is, e.g. a bakery with online orders>"
disable-model-invocation: true
---

# New SkyNet website

Brief: **$ARGUMENTS**

Load the `skynet:website` skill (and `skynet:art`, `skynet:verify`; `skynet:sql` if the site needs a database) before planning.

## Step 1 - Plan (no files yet)

Reply with a compact plan:

- **Brand:** an invented name, one-line idea, palette (ink, background, accent + one or two more), display and text fonts with fallbacks.
- **Pages:** table of page, two-letter prefix, purpose, server methods.
- **Key features:** what the server calculates or validates, and what each form saves and where.
- **Data:** `data/site.json` sections, or SQL tables (then follow the `sql` skill).
- **Staff area (if any):** admin pages, roles with the areas each manages, and what is logged (follow `reference/admin.md` of the `website` skill). The first admin password is made on first start and shown on the sign-in page on the developer's computer.
- **Images:** count and styles from the `art` skill.
- **Questions:** at most three, only if the answer changes what you build.

Then stop and wait for the user to say "go". Apply any changes they ask for first.

## Step 2 - Build (after "go")

1. Copy `${CLAUDE_SKILL_DIR}/../website/starter/` into the new project folder (named after the project, PascalCase). Rename `Starter.csproj`, `RootNamespace`, every `Starter.` namespace, the app name in `appConfig/application.cfg`, and pick new ports in `Properties/launchSettings.json`. Remove the starter's pages and images you do not reuse.
2. Write `data/site.json` and `codes/Models/<Project>Model.cs`.
3. Build each page: `htmls/X.html`, `styles/X.css`, `codes/X.cs`, `scripts/X.js`, following `reference/page-model.md` and `reference/pitfalls.md` of the `website` skill.
4. Paint the images with the `art` skill; check a contact sheet and fix weak ones.
5. Copy the `LICENSE` from the plugin root if the user wants the MIT template license; write `README.md` from `reference/readme-template.md` with real counts.

## Step 3 - Verify

Run every step of the `skynet:verify` skill: source checks, compile, screenshots at 1440/820/390 (look at them), interaction tests for every server method. Fix and repeat until all pass.

## Step 4 - Report

Short summary: pages, features, the verification table, and `cd <project> && dotnet run`.
