package core.metamodel.org.apache.isis.core.metamodel.facets.object.callbacks;

public abstract class LoadedCallbackFacetAbstract extends CallbackFacetAbstract implements LoadedCallbackFacet { public static Class < ? extends Facet > type ( ) { return LoadedCallbackFacet . class ; } public LoadedCallbackFacetAbstract ( final FacetHolder holder ) { super ( type ( ) , holder ) ; } }