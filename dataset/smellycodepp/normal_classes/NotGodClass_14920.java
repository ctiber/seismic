package clients.org.apache.kafka.common.errors;

public class NotEnoughReplicasAfterAppendException extends RetriableException { private static final long serialVersionUID = 1L ; public NotEnoughReplicasAfterAppendException ( String message ) { super ( message ) ; } }