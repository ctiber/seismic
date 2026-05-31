package clients.org.apache.kafka.common.errors;

public class InvalidTimestampException extends ApiException { private static final long serialVersionUID = 1L ; public InvalidTimestampException ( String message ) { super ( message ) ; } public InvalidTimestampException ( String message , Throwable cause ) { super ( message , cause ) ; } }