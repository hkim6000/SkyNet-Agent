---
name: sql
description: Generic SQL Server data access for SkyNet pages - the Helper.cs data layer (PutData, GetDataTable, GetListT, GetOneT) over SkyNet's SQLData, parameterized queries, list/edit/save/delete page pattern and table scripts. Use when a SkyNet page reads or writes a database, or when the user runs /skynet:sql-page.
user-invocable: false
---

# SkyNet SQL: generic Get and Put

SkyNet talks to SQL Server through `SQLData`. Every project gets one shared file, `codes/Helper.cs`, that wraps it; pages call the helper and never build connections themselves.

## Files

| File | What it is |
|---|---|
| [sample/codes/Helper.cs](sample/codes/Helper.cs) | The data layer. Copy it into `codes/` and change the namespace |
| [sample/codes/Item.cs](sample/codes/Item.cs) + `htmls/`, `scripts/`, `styles/` | A complete list / add / edit / delete page |
| [sample/codes/Models/MyAppModel.cs](sample/codes/Models/MyAppModel.cs) | The DTO used by `GetListT<T>` |
| [sample/database/ITEM.sql](sample/database/ITEM.sql) | Table script with sample rows |

## Connection

`SQLData` reads the connection from `appConfig/application.cfg`:

```
app.sqldb.source | (local)
app.sqldb.catalog | MyApp
app.sqldb.id | sa
app.sqldb.password | your-password
app.sqldb.timeout | 3600
```

Keep `your-password` in anything you commit or publish. If `Microsoft.Data.SqlClient` types are not found, add the package: `dotnet add package Microsoft.Data.SqlClient`.

## The helper

```csharp
string result = await Helper.PutData(sqls, parameters);
var (dt, emsg) = await Helper.GetDataTable(sql, parameters);
var (list, emsg) = await Helper.GetListT<ItemRow>(sql, parameters);
var (item, emsg) = await Helper.GetOneT<ItemRow>(sql, parameters);
if (Helper.IsError(result)) { ... }
```

- **Reads** return a tuple: check `emsg` first (empty means success), then the data.
- **Writes** pass a list of SQL statements and one shared parameter list; the result is a message that starts with `Error:` on failure.
- **`GetListT<T>`** maps each row to a new `T` by name. Keep DTO property names identical to the SELECT column names, using aliases: `SELECT ITEM_ID AS ItemId, ITEM_NAME AS Name ...`.
- **`GetOneT<T>`** returns the first row or `null`.
- `GetDataTable` is for checks and custom shapes (`SELECT 1 ... ` duplicate checks, aggregates).

## Rules

1. **Always parameterize.** Every value from the user goes in a `SqlParameter` with an explicit type and size; never concatenate user input into SQL text.
   ```csharp
   new SqlParameter("name", SqlDbType.NVarChar) { Size = 100, Value = name }
   new SqlParameter("price", SqlDbType.Decimal) { Precision = 18, Scale = 2, Value = price }
   new SqlParameter("hired", SqlDbType.Date) { Value = ok ? date : (object)DBNull.Value }
   ```
2. **Validate on the server first.** Trim, check lengths, ranges and allowed values, and fill each field's error element; only then touch the database.
3. **Unicode text:** `NVARCHAR` columns and `N'...'` literals.
4. **Keys:** `NVARCHAR(50)` ids from `Guid.NewGuid().ToString()` generated in C#, so the page knows the id before inserting.
5. **Audit column:** `SYSDTE DATETIME DEFAULT GETDATE()`, set again on every update.
6. **Errors:** show database errors with `response.ModalWindow("Error", emsg)`; show "not found" kindly; never show stack traces.
7. **Output:** every value written into HTML goes through `HtmlEncode`; one record for a form goes to the browser with `SetVariableData("item", new { id = ..., name = ... })` and is read with `$GetVarData('item')` in an `ExecuteScript` callback. Use explicit lower-case property names in that anonymous object.
8. **Lists:** render rows in C# (`StringBuilder`), put a lower-case `data-search` attribute on each row for instant client-side filtering, and re-render with a `Refresh()` method after saves and deletes.
9. **One helper only.** `codes/Helper.cs` is the single shared C# file besides the models; keep page logic inside each page.

## Page pattern (see Item.cs)

| Server method | Does |
|---|---|
| `OnInitialized()` | `GetListT` → rows into `{plhd_rows}` and count into `{plhd_count}` |
| `Refresh()` | the same list, returned with `SetElementContents` |
| `GetItem()` | `GetOneT` by id → `SetVariableData` → `ItemJs.onItem(...)` fills the form |
| `SaveItem()` | validate → duplicate check → `INSERT` or `UPDATE` with `PutData` → `ItemJs.onSaved(isNew)` |
| `DeleteItem()` | `DELETE` by id with `PutData` → `ItemJs.onDeleted()` |

Request keys (`id`, `name`, `price`...) must not equal any query-string name the page reads with `QueryValue` (see the `website` skill, pitfalls).
