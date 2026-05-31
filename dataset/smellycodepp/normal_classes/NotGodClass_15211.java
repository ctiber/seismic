package tools.org.apache.kafka.trogdor.rest;

public class DestroyTaskRequest extends Message { private final String id ; @ JsonCreator public DestroyTaskRequest ( @ JsonProperty ( "id" ) String id ) { this . id = id ; } @ JsonProperty public String id ( ) { return id ; } }