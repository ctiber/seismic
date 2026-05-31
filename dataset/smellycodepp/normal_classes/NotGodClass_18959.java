package exec.jdbc.org.apache.drill.jdbc.proxy;

class ProxySetupSQLException extends SQLNonTransientConnectionException { private static final long serialVersionUID = 2015_02_08L ; ProxySetupSQLException ( String message , Throwable cause ) { super ( message , cause ) ; } ProxySetupSQLException ( String message ) { super ( message ) ; } }