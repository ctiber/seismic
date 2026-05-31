package src.org.apache.cocoon.util;

public class JavaArchiveFilter implements FileFilter { public boolean accept ( File file ) { String name = file . getName ( ) . toLowerCase ( ) ; return ( name . endsWith ( ".jar" ) || name . endsWith ( ".zip" ) ) ; } }