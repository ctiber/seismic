package server.base.org.apache.accumulo.server.master.state;

public class DistributedStoreException extends Exception { private static final long serialVersionUID = 1L ; public DistributedStoreException ( String why ) { super ( why ) ; } public DistributedStoreException ( Exception cause ) { super ( cause ) ; } }