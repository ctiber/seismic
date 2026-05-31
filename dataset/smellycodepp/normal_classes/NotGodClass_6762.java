package src.org.apache.nutch.plugin;

public class CircularDependencyException extends Exception { private static final long serialVersionUID = 1L ; public CircularDependencyException ( Throwable cause ) { super ( cause ) ; } public CircularDependencyException ( String message ) { super ( message ) ; } }