package jdbc.org.apache.kylin.jdbc;

public class KylinStatement extends AvaticaStatement { protected KylinStatement ( AvaticaConnection connection , StatementHandle h , int resultSetType , int resultSetConcurrency , int resultSetHoldability ) { super ( connection , h , resultSetType , resultSetConcurrency , resultSetHoldability ) ; } }