package src.blocks.portal.org.apache.cocoon.portal.pluto.om.common;

public static class Unmodifiable extends UnmodifiableSet implements SecurityRoleRefSet { public Unmodifiable ( SecurityRoleRefSet c ) { super ( c ) ; } public SecurityRoleRef get ( String roleName ) { return ( ( SecurityRoleRefSet ) c ) . get ( roleName ) ; } }