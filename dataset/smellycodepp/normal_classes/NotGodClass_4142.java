package java.org.apache.catalina.mbeans;

public static class RmiServerBindSocketFactory implements RMIServerSocketFactory { private final InetAddress bindAddress ; public RmiServerBindSocketFactory ( InetAddress address ) { bindAddress = address ; } @ Override public ServerSocket createServerSocket ( int port ) throws IOException { return new ServerSocket ( port , 0 , bindAddress ) ; } }