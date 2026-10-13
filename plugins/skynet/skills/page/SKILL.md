---
name: page
description: Add one page to an existing SkyNet project - plan it, wait for "go", then write the four files (C#, HTML, JS, CSS) in the project's own style and verify.
argument-hint: "<PageName> <what the page does>"
disable-model-invocation: true
---

# Add a SkyNet page

Request: **$ARGUMENTS**

Load the `skynet:website` skill first.

## Step 1 - Study the project (read only)

- Find the `.csproj`, `RootNamespace`, `codes/`, `htmls/`, `scripts/`, `styles/`, `data/` and the model file.
- Read one or two existing pages completely: header and footer markup, CSS variables, the JS namespace pattern, C# helpers, how data is loaded.
- List the prefixes already used so the new one is unique.

## Step 2 - Plan (no files yet)

Reply with: page name and URL, prefix, sections, server methods (name, request keys, what each returns), data it reads or writes, and any change needed in other pages (for example a menu link). Wait for "go".

## Step 3 - Build (after "go")

- Create `codes/X.cs`, `htmls/X.html`, `scripts/X.js`, `styles/X.css`, copying the project's header, footer and shared styles with the new prefix.
- Add the menu link to the other pages only if the plan said so, and touch nothing else in them.
- Request keys must not equal any query-string name the page reads.

## Step 4 - Verify

Run the `skynet:verify` skill for the new page (source checks, compile, screenshots at three widths, interaction tests for its methods) and for any page you edited.
