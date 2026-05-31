package org.apache.commons.io.input;

public class CloseShieldInputStream extends ProxyInputStream { public CloseShieldInputStream ( final InputStream in ) { super ( in ) ; } @ Override public void close ( ) { in = new ClosedInputStream ( ) ; } }