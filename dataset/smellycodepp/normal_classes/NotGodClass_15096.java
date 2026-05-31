package connect.api.org.apache.kafka.connect.errors;

public class NotFoundException extends ConnectException { public NotFoundException ( String s ) { super ( s ) ; } public NotFoundException ( String s , Throwable throwable ) { super ( s , throwable ) ; } public NotFoundException ( Throwable throwable ) { super ( throwable ) ; } }