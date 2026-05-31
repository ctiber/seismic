package unixauthclient.org.apache.ranger.authentication.unix.jaas;

public class UnixUserPrincipal implements Principal , Serializable { private static final long serialVersionUID = - 3568658536591178268L ; private String userName ; public UnixUserPrincipal ( String userName ) { this . userName = userName ; } @ Override public String getName ( ) { return userName ; } }