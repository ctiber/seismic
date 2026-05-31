package clients.org.apache.kafka.common.errors;

public class TopicExistsException extends ApiException { private static final long serialVersionUID = 1L ; public TopicExistsException ( String message ) { super ( message ) ; } public TopicExistsException ( String message , Throwable cause ) { super ( message , cause ) ; } }