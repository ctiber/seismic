package modules.security.org.apache.airavata.security.configurations;

public class AuthenticatorComparator implements Comparator < Authenticator > { @ Override public int compare ( Authenticator o1 , Authenticator o2 ) { return ( o1 . getPriority ( ) > o2 . getPriority ( ) ? - 1 : ( o1 . getPriority ( ) == o2 . getPriority ( ) ? 0 : 1 ) ) ; } }