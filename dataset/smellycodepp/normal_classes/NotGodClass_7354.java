package core.org.apache.calcite.sql.dialect;

public class InformixSqlDialect extends SqlDialect { public static final SqlDialect DEFAULT = new InformixSqlDialect ( EMPTY_CONTEXT . withDatabaseProduct ( DatabaseProduct . INFORMIX ) ) ; public InformixSqlDialect ( Context context ) { super ( context ) ; } }