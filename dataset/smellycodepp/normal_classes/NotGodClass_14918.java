package clients.org.apache.kafka.common.errors;

public class NotControllerException extends RetriableException { private static final long serialVersionUID = 1L ; public NotControllerException ( String message ) { super ( message ) ; } public NotControllerException ( String message , Throwable cause ) { super ( message , cause ) ; } }