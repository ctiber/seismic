package hcatalog.streaming.src.org.apache.hive.hcatalog.streaming;

public class PartitionCreationFailed extends StreamingException { public PartitionCreationFailed ( HiveEndPoint endPoint , Exception cause ) { super ( "Failed to create partition " + endPoint , cause ) ; } }