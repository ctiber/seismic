package query.org.apache.kylin.query.udf;

public class VersionUDF { public String eval ( ) { return KylinVersion . getCurrentVersion ( ) . toString ( ) ; } }