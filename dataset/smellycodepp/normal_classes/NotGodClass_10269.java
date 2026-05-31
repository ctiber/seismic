package testutils.ptest2.org.apache.hive.ptest.execution;

public class AbortDroneException extends Exception { private static final long serialVersionUID = 6673699997331155666L ; public AbortDroneException ( String msg ) { this ( msg , null ) ; } public AbortDroneException ( String msg , Throwable throwable ) { super ( msg , throwable ) ; } }