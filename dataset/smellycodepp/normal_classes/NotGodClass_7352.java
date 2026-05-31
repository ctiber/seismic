package core.org.apache.calcite.sql.dialect;

public class FirebirdSqlDialect extends SqlDialect { public static final SqlDialect DEFAULT = new FirebirdSqlDialect ( EMPTY_CONTEXT . withDatabaseProduct ( DatabaseProduct . FIREBIRD ) ) ; public FirebirdSqlDialect ( Context context ) { super ( context ) ; } }