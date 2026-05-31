package rt.ws.policy.org.apache.cxf.ws.policy.blueprint;

public static class PassThroughCallable < T > implements Callable < T > { private T value ; public PassThroughCallable ( T value ) { this . value = value ; } public T call ( ) throws Exception { return value ; } }