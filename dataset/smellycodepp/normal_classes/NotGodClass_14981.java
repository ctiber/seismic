package clients.org.apache.kafka.common.errors;

public class UnknownLeaderEpochException extends RetriableException { private static final long serialVersionUID = 1L ; public UnknownLeaderEpochException ( String message ) { super ( message ) ; } public UnknownLeaderEpochException ( String message , Throwable cause ) { super ( message , cause ) ; } }