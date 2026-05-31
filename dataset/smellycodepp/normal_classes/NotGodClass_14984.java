package clients.org.apache.kafka.common.errors;

public class UnsupportedCompressionTypeException extends ApiException { private static final long serialVersionUID = 1L ; public UnsupportedCompressionTypeException ( String message ) { super ( message ) ; } public UnsupportedCompressionTypeException ( String message , Throwable cause ) { super ( message , cause ) ; } }