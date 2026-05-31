package clients.org.apache.kafka.common.errors;

public class ControllerMovedException extends ApiException { private static final long serialVersionUID = 1L ; public ControllerMovedException ( String message ) { super ( message ) ; } public ControllerMovedException ( String message , Throwable cause ) { super ( message , cause ) ; } }