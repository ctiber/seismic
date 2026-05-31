package metastore.src.org.apache.hadoop.hive.metastore.events;

public class PreCreateTableEvent extends PreEventContext { private final Table table ; public PreCreateTableEvent ( Table table , HMSHandler handler ) { super ( PreEventType . CREATE_TABLE , handler ) ; this . table = table ; } public Table getTable ( ) { return table ; } }