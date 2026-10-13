using System.Data;
using System.Reflection;
using Microsoft.Data.SqlClient;

namespace SkyNet
{
    public class ApiResponse
    {
        public List<(string op, string k, string v)> Ops { get; } = new();
        public void SetElementContents(string elementId, string contentsHtml) => Ops.Add(("set", elementId, contentsHtml));
        public void ExecuteScript(string jsScripts) => Ops.Add(("js", "", jsScripts));
        public void ModalWindow(string title, string message) => Ops.Add(("js", "", "alert(" + System.Text.Json.JsonSerializer.Serialize(title + "\n" + message) + ");"));
        public void SetVariableData<T>(string name, T data) => Ops.Add(("var", name, System.Text.Json.JsonSerializer.Serialize(data)));
    }

    public class HtmlDocument
    {
        public string HtmlBodyText { get; set; } = string.Empty;
        public string Title = "";
        public List<string> Meta = new();
        public void SetTitle(string pageTitle) => Title = pageTitle;
        public void AddMetaElement(string name, string contents) => Meta.Add(name + "=" + contents);
        public void AddCSSFile(string file) => Meta.Add("css=" + file);
        public void AddJsFile(string file) => Meta.Add("js=" + file);
    }

    public class WebCore
    {
        public static Dictionary<string, string> Data = new();
        public static Dictionary<string, string> Query = new();
        public string DataPath { get; set; } = string.Empty;
        public string QueryValue(string key, bool decode = false) => Query.TryGetValue(key, out var v) ? v : string.Empty;
        public string GetDataValue(string key) => Data.TryGetValue(key, out var v) ? v : string.Empty;
        public static string HtmlEncode(string value) => System.Net.WebUtility.HtmlEncode(value);

        public List<T> DataTableListT<T>(DataTable dt)
        {
            List<T> list = new();
            PropertyInfo[] props = typeof(T).GetProperties();
            foreach (DataRow r in dt.Rows)
            {
                T item = Activator.CreateInstance<T>();
                foreach (PropertyInfo p in props)
                {
                    if (dt.Columns.Contains(p.Name) && r[p.Name] != DBNull.Value)
                    {
                        Type t = Nullable.GetUnderlyingType(p.PropertyType) ?? p.PropertyType;
                        p.SetValue(item, Convert.ChangeType(r[p.Name], t));
                    }
                }
                list.Add(item);
            }
            return list;
        }
    }

    public class WebPage : WebCore
    {
        public HtmlDocument HtmlDoc { get; set; } = new();
        public virtual Task OnInitialized() => Task.CompletedTask;
    }

    public class SQLInfo
    {
    }

    public class SQLData
    {
        public SQLData()
        {
        }

        public SQLData(SQLInfo info)
        {
        }

        public Task<(DataTable dt, string emsg)> GetDataAsync(string sql, List<SqlParameter>? parameters = null) => Task.FromResult((new DataTable(), string.Empty));
        public Task<string> PutDataAsync(List<string> sqls, List<SqlParameter>? parameters = null) => Task.FromResult(string.Empty);
    }
}
