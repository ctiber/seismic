package api.org.apache.cxf;

public class BusException extends org . apache . cxf . common . i18n . Exception { private static final long serialVersionUID = 1L ; public BusException ( Message msg ) { super ( msg ) ; } public BusException ( Message msg , Throwable cause ) { super ( msg , cause ) ; } public BusException ( Throwable cause ) { super ( cause ) ; } }