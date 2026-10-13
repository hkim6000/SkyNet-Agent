using System.Data;
using System.Globalization;
using System.Text;
using Microsoft.Data.SqlClient;
using MyApp.Models;
using SkyNet;

namespace MyApp.codes
{
    public class Item : WebPage
    {
        private const string ListSql = @"SELECT ITEM_ID AS ItemId, ITEM_NAME AS Name, CATEGORY AS Category, PRICE AS Price, STOCK AS Stock, ACTIVE AS Active
                                         FROM ITEM
                                         ORDER BY ACTIVE DESC, ITEM_NAME";

        public override async Task OnInitialized()
        {
            HtmlDoc.SetTitle("Items");
            HtmlDoc.AddMetaElement("viewport", "width=device-width, initial-scale=1");

            var (rows, emsg) = await Helper.GetListT<ItemRow>(ListSql);
            HtmlDoc.HtmlBodyText = HtmlDoc.HtmlBodyText
                .Replace("{plhd_rows}", emsg == string.Empty ? Rows(rows ?? new List<ItemRow>()) : ErrorRow(emsg))
                .Replace("{plhd_count}", emsg == string.Empty ? CountText((rows ?? new List<ItemRow>()).Count) : string.Empty);
        }

        public async Task<ApiResponse> Refresh()
        {
            ApiResponse response = new ApiResponse();
            var (rows, emsg) = await Helper.GetListT<ItemRow>(ListSql);
            if (emsg != string.Empty)
            {
                response.ModalWindow("Error", emsg);
                return response;
            }
            response.SetElementContents("it-rows", Rows(rows ?? new List<ItemRow>()));
            response.SetElementContents("it-count", CountText((rows ?? new List<ItemRow>()).Count));
            return response;
        }

        public async Task<ApiResponse> GetItem()
        {
            ApiResponse response = new ApiResponse();
            var (item, emsg) = await Helper.GetOneT<ItemRow>(
                @"SELECT ITEM_ID AS ItemId, ITEM_NAME AS Name, CATEGORY AS Category, PRICE AS Price, STOCK AS Stock, ACTIVE AS Active
                  FROM ITEM
                  WHERE ITEM_ID = @id",
                new List<SqlParameter> { new SqlParameter("id", SqlDbType.NVarChar) { Size = 50, Value = GetDataValue("id") ?? string.Empty } });
            if (emsg != string.Empty)
            {
                response.ModalWindow("Error", emsg);
                return response;
            }
            if (item == null)
            {
                response.ModalWindow("Not found", "This item no longer exists.");
                return response;
            }
            response.SetVariableData("item", new { id = item.ItemId, name = item.Name, category = item.Category, price = item.Price, stock = item.Stock, active = item.Active });
            response.ExecuteScript("ItemJs.onItem($GetVarData('item'));");
            return response;
        }

        public async Task<ApiResponse> SaveItem()
        {
            ApiResponse response = new ApiResponse();
            string id = (GetDataValue("id") ?? string.Empty).Trim();
            bool isNew = id == string.Empty;
            if (isNew)
            {
                id = Guid.NewGuid().ToString();
            }
            string name = (GetDataValue("name") ?? string.Empty).Trim();
            string category = (GetDataValue("category") ?? string.Empty).Trim();
            bool priceOk = decimal.TryParse(GetDataValue("price"), NumberStyles.Number, CultureInfo.InvariantCulture, out decimal price);
            bool stockOk = int.TryParse(GetDataValue("stock"), NumberStyles.Integer, CultureInfo.InvariantCulture, out int stock);
            bool active = GetDataValue("active") == "1";

            string eName = name.Length < 2 || name.Length > 100 ? "Enter a name (2 to 100 characters)." : string.Empty;
            string eCategory = category.Length > 50 ? "Use 50 characters or fewer." : string.Empty;
            string ePrice = !priceOk || price < 0 || price > 1000000 ? "Enter a price from 0 to 1,000,000." : string.Empty;
            string eStock = !stockOk || stock < 0 ? "Enter a stock count of 0 or more." : string.Empty;
            response.SetElementContents("it-e-name", eName);
            response.SetElementContents("it-e-category", eCategory);
            response.SetElementContents("it-e-price", ePrice);
            response.SetElementContents("it-e-stock", eStock);
            if (eName + eCategory + ePrice + eStock != string.Empty)
            {
                return response;
            }

            var (dup, derr) = await Helper.GetDataTable(
                "SELECT 1 FROM ITEM WHERE ITEM_NAME = @name AND ITEM_ID <> @id",
                new List<SqlParameter>
                {
                    new SqlParameter("name", SqlDbType.NVarChar) { Size = 100, Value = name },
                    new SqlParameter("id", SqlDbType.NVarChar) { Size = 50, Value = id }
                });
            if (derr != string.Empty)
            {
                response.ModalWindow("Error", derr);
                return response;
            }
            if (dup.Rows.Count > 0)
            {
                response.SetElementContents("it-e-name", "Another item already uses this name.");
                return response;
            }

            List<SqlParameter> parameters = new List<SqlParameter>
            {
                new SqlParameter("id", SqlDbType.NVarChar) { Size = 50, Value = id },
                new SqlParameter("name", SqlDbType.NVarChar) { Size = 100, Value = name },
                new SqlParameter("category", SqlDbType.NVarChar) { Size = 50, Value = category },
                new SqlParameter("price", SqlDbType.Decimal) { Precision = 18, Scale = 2, Value = price },
                new SqlParameter("stock", SqlDbType.Int) { Value = stock },
                new SqlParameter("active", SqlDbType.Bit) { Value = active }
            };
            List<string> sqls = new List<string>
            {
                isNew
                    ? @"INSERT INTO ITEM (ITEM_ID, ITEM_NAME, CATEGORY, PRICE, STOCK, ACTIVE, SYSDTE)
                        VALUES (@id, @name, @category, @price, @stock, @active, GETDATE())"
                    : @"UPDATE ITEM SET ITEM_NAME = @name, CATEGORY = @category, PRICE = @price, STOCK = @stock, ACTIVE = @active, SYSDTE = GETDATE()
                        WHERE ITEM_ID = @id"
            };
            string result = await Helper.PutData(sqls, parameters);
            if (Helper.IsError(result))
            {
                response.ModalWindow("Error", result);
                return response;
            }
            response.ExecuteScript("ItemJs.onSaved(" + (isNew ? "true" : "false") + ");");
            return response;
        }

        public async Task<ApiResponse> DeleteItem()
        {
            ApiResponse response = new ApiResponse();
            string result = await Helper.PutData(
                new List<string> { "DELETE FROM ITEM WHERE ITEM_ID = @id" },
                new List<SqlParameter> { new SqlParameter("id", SqlDbType.NVarChar) { Size = 50, Value = GetDataValue("id") ?? string.Empty } });
            if (Helper.IsError(result))
            {
                response.ModalWindow("Error", result);
                return response;
            }
            response.ExecuteScript("ItemJs.onDeleted();");
            return response;
        }

        private static string Rows(List<ItemRow> rows)
        {
            if (rows.Count == 0)
            {
                return "<tr><td colspan=\"5\" class=\"it-empty\">No items yet. Add the first one.</td></tr>";
            }
            StringBuilder sb = new StringBuilder();
            foreach (ItemRow r in rows)
            {
                string search = (r.Name + " " + r.Category).ToLowerInvariant();
                sb.Append("<tr data-search=\"" + HtmlEncode(search) + "\" onclick=\"ItemJs.edit('" + HtmlEncode(r.ItemId) + "')\">");
                sb.Append("<td class=\"it-c-name\">" + HtmlEncode(r.Name) + "</td>");
                sb.Append("<td>" + HtmlEncode(r.Category) + "</td>");
                sb.Append("<td class=\"it-num\">" + r.Price.ToString("#,0.00", CultureInfo.InvariantCulture) + "</td>");
                sb.Append("<td class=\"it-num" + (r.Stock == 0 ? " it-out" : string.Empty) + "\">" + r.Stock.ToString("#,0", CultureInfo.InvariantCulture) + "</td>");
                sb.Append("<td><span class=\"it-status " + (r.Active ? "it-on" : "it-off") + "\">" + (r.Active ? "Active" : "Inactive") + "</span></td></tr>");
            }
            return sb.ToString();
        }

        private static string ErrorRow(string emsg)
        {
            return "<tr><td colspan=\"5\" class=\"it-empty\">" + HtmlEncode(emsg) + "</td></tr>";
        }

        private static string CountText(int n)
        {
            return n == 1 ? "1 item" : n.ToString("#,0", CultureInfo.InvariantCulture) + " items";
        }
    }
}
