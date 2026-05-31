package ql.src.org.apache.hadoop.hive.ql.security.authorization;

public class DefaultHiveAuthorizationProvider extends BitSetCheckedAuthorizationProvider { public void init ( Configuration conf ) throws HiveException { hive_db = new HiveProxy ( Hive . get ( new HiveConf ( conf , HiveAuthorizationProvider . class ) ) ) ; } }