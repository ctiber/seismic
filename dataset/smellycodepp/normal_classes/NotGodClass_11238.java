package integration.spark.scala.org.apache.spark.sql.secondaryindex.exception;

public class IndexTableExistException extends Exception { private static final long serialVersionUID = 1L ; private String msg ; public IndexTableExistException ( String msg ) { super ( msg ) ; this . msg = msg ; } @ Override public String getMessage ( ) { return this . msg ; } }