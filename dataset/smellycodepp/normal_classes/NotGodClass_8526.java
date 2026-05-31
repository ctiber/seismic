package itests.util.org.apache.hadoop.hive.hbase;

public class HBaseQTestUtil extends QTestUtil { public HBaseQTestUtil ( String outDir , String logDir , MiniClusterType miniMr , HBaseTestSetup setup ) throws Exception { super ( outDir , logDir , miniMr , null ) ; setup . preTest ( conf ) ; super . init ( ) ; } @ Override public void init ( ) throws Exception { } }