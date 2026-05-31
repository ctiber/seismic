package rt.core.org.apache.cxf.interceptor.security;

public class AuthenticationException extends SecurityException { private static final long serialVersionUID = - 823479120896894071L ; public AuthenticationException ( ) { } public AuthenticationException ( String reason ) { super ( reason ) ; } }