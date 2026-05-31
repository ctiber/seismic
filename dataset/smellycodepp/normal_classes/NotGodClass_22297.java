package core.org.apache.shiro.dao;

public abstract class DataAccessException extends ShiroException { public DataAccessException ( String message ) { super ( message ) ; } public DataAccessException ( String message , Throwable cause ) { super ( message , cause ) ; } }