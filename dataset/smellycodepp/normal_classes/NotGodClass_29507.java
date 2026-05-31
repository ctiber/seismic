package org.apache.commons.dbcp2;

private class PaGetConnection implements PrivilegedExceptionAction < Connection > { @ Override public Connection run ( ) throws SQLException { return createDataSource ( ) . getConnection ( ) ; } }