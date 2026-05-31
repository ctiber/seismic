package server.tserver.org.apache.accumulo.tserver.tablet;

public class TabletClosedException extends RuntimeException { public TabletClosedException ( Exception e ) { super ( e ) ; } public TabletClosedException ( ) { super ( ) ; } private static final long serialVersionUID = 1L ; }