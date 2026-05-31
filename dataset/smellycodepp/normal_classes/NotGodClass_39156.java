package core.metamodel.org.apache.isis.core.metamodel.facets.object.callbacks;

public abstract class CreatedCallbackFacetAbstract extends CallbackFacetAbstract implements CreatedCallbackFacet { public static Class < ? extends Facet > type ( ) { return CreatedCallbackFacet . class ; } public CreatedCallbackFacetAbstract ( final FacetHolder holder ) { super ( type ( ) , holder ) ; } }