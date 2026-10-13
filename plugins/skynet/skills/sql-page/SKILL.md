---
name: sql-page
description: Add a database page (list, add, edit, delete) to a SkyNet project using the generic Helper.cs data layer and parameterized SQL Server queries - plan the table and page, wait for "go", then build, script the table and verify.
argument-hint: "<PageName> <table and fields, e.g. Customers: name, email, phone, status>"
disable-model-invocation: true
---

# Add a SkyNet database page

Request: **$ARGUMENTS**

Load the `skynet:website` and `skynet:sql` skills first.

## Step 1 - Study (read only)

- Check for `codes/Helper.cs`. If it is missing, plan to copy `${CLAUDE_SKILL_DIR}/../sql/sample/codes/Helper.cs` (change the namespace).
- Check `appConfig/application.cfg` for the `app.sqldb.*` keys.
- Read an existing page for the project's style.

## Step 2 - Plan (no files yet)

Reply with:

- **Table:** name, columns with SQL types and sizes, key, defaults, unique indexes, `SYSDTE`.
- **DTO:** class name and properties (they match the SELECT aliases).
- **Page:** name, prefix, list columns, form fields with validation rules.
- **Server methods:** `OnInitialized`, `Refresh`, `Get<X>`, `Save<X>`, `Delete<X>` (plus any filters).

Wait for "go".

## Step 3 - Build (after "go")

- `database/<TABLE>.sql`: `CREATE TABLE`, indexes and a few fictional sample rows.
- The DTO in the project's model file.
- `codes/X.cs`, `htmls/X.html`, `scripts/X.js`, `styles/X.css` following `sql/sample/` (Item page) and the project's own look.
- Every value through `SqlParameter` with type and size; server-side validation before any write; `ModalWindow` for database errors.

## Step 4 - Verify

Run the `skynet:verify` skill. Without a database the page must still render and show the error or empty state cleanly. Tell the user to run the table script and set the `app.sqldb.*` keys, and list the manual tests to do once connected (add, edit, duplicate name, delete).
