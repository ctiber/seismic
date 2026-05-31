package hcatalog.webhcat.svr.org.apache.hive.hcatalog.templeton;

public class CallbackFailedException extends SimpleWebException { public CallbackFailedException ( String msg ) { super ( HttpStatus . BAD_REQUEST_400 , msg ) ; } }