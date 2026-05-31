package framework.base.src.org.ofbiz.base.location;

public class StandardUrlLocationResolver implements LocationResolver { public URL resolveLocation ( String location ) throws MalformedURLException { return new URL ( location ) ; } }