package core.org.apache.calcite.adapter.jdbc;

public final class JdbcQueryProvider extends QueryProviderImpl { public static final JdbcQueryProvider INSTANCE = new JdbcQueryProvider ( ) ; private JdbcQueryProvider ( ) { } public < T > Enumerator < T > executeQuery ( Queryable < T > queryable ) { return null ; } }