package hcatalog.webhcat.svr.org.apache.hive.hcatalog.templeton;

public class NotAuthorizedException extends SimpleWebException { public NotAuthorizedException ( String msg ) { super ( HttpStatus . UNAUTHORIZED_401 , msg ) ; } }