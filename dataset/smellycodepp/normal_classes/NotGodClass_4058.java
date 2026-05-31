package java.org.apache.catalina.ant;

public class ServerinfoTask extends AbstractCatalinaTask { @ Override public void execute ( ) throws BuildException { super . execute ( ) ; execute ( "/serverinfo" ) ; } }