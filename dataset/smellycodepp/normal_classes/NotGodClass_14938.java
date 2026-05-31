package clients.org.apache.kafka.common.errors;

public class UnsupportedForMessageFormatException extends ApiException { private static final long serialVersionUID = 1L ; public UnsupportedForMessageFormatException ( String message ) { super ( message ) ; } public UnsupportedForMessageFormatException ( String message , Throwable cause ) { super ( message , cause ) ; } }