using System.Data;
using Microsoft.Data.SqlClient;
using SkyNet;

namespace MyApp.codes
{
    public static class Helper
    {
        public static async Task<string> PutData(List<string> sSql, List<SqlParameter>? parameters = null)
        {
            SQLData msql = new SQLData();
            string result = await msql.PutDataAsync(sSql, parameters);
            return result;
        }

        public static async Task<(DataTable dt, string emsg)> GetDataTable(string sSql, List<SqlParameter>? parameters = null)
        {
            SQLData msql = new SQLData();
            var (dt, emsg) = await msql.GetDataAsync(sSql, parameters);
            return (dt, emsg);
        }

        public static async Task<(List<T>? data, string emsg)> GetListT<T>(string sSql, List<SqlParameter>? parameters = null)
        {
            SQLData msql = new SQLData();
            var (dt, emsg) = await msql.GetDataAsync(sSql, parameters);
            if (!string.IsNullOrEmpty(emsg))
            {
                return (null, emsg);
            }
            WebCore webcore = new WebCore();
            List<T> data = webcore.DataTableListT<T>(dt);
            return (data, string.Empty);
        }

        public static async Task<(T? data, string emsg)> GetOneT<T>(string sSql, List<SqlParameter>? parameters = null)
        {
            var (list, emsg) = await GetListT<T>(sSql, parameters);
            if (!string.IsNullOrEmpty(emsg))
            {
                return (default, emsg);
            }
            return (list != null && list.Count > 0 ? list[0] : default, string.Empty);
        }

        public static bool IsError(string result)
        {
            return result.StartsWith("Error:", StringComparison.OrdinalIgnoreCase);
        }
    }
}
