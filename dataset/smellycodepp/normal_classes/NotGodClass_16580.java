package src.org.apache.cocoon.components.store.impl;

public class DefaultStore extends MRUMemoryStore { public void parameterize ( Parameters params ) throws ParameterException { if ( ! params . isParameter ( "use-persistent-cache" ) ) { params . setParameter ( "use-persistent-cache" , "true" ) ; } super . parameterize ( params ) ; } }