package tools.org.apache.kafka.trogdor.fault;

public class ProcessStopFaultController implements TaskController { private final Set < String > nodeNames ; public ProcessStopFaultController ( Set < String > nodeNames ) { this . nodeNames = nodeNames ; } @ Override public Set < String > targetNodes ( Topology topology ) { return nodeNames ; } }