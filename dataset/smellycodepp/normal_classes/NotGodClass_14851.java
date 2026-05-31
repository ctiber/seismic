package clients.org.apache.kafka.clients.admin;

public abstract class AbstractOptions < T extends AbstractOptions > { protected Integer timeoutMs = null ; @ SuppressWarnings ( "unchecked" ) public T timeoutMs ( Integer timeoutMs ) { this . timeoutMs = timeoutMs ; return ( T ) this ; } public Integer timeoutMs ( ) { return timeoutMs ; } }