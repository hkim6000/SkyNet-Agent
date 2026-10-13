using System.Data;

namespace Microsoft.Data.SqlClient
{
    public class SqlParameter
    {
        public SqlParameter(string name, SqlDbType type)
        {
            ParameterName = name;
            SqlDbType = type;
        }

        public string ParameterName { get; set; }
        public SqlDbType SqlDbType { get; set; }
        public int Size { get; set; }
        public byte Precision { get; set; }
        public byte Scale { get; set; }
        public object? Value { get; set; }
    }
}
