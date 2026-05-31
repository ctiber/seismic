package rt.frontend.jaxrs.org.apache.cxf.jaxrs.blueprint;

public static class PassThroughCallable < T > implements Callable < T > { private T value ; public PassThroughCallable ( T value ) { this . value = value ; } public T call ( ) throws Exception { return value ; } }