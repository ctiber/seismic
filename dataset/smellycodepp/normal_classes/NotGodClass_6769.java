package src.org.apache.nutch.protocol;

@ SuppressWarnings ( "serial" ) public class ProtocolNotFound extends ProtocolException { private String url ; public ProtocolNotFound ( String url ) { this ( url , "protocol not found for url=" + url ) ; } public ProtocolNotFound ( String url , String message ) { super ( message ) ; this . url = url ; } public String getUrl ( ) { return url ; } }