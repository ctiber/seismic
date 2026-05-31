package core.metamodel.org.apache.isis.core.metamodel.facets;

public abstract class MultipleValueFacetAbstract extends FacetAbstract implements MultipleValueFacet { public MultipleValueFacetAbstract ( final Class < ? extends Facet > facetType , final FacetHolder holder ) { super ( facetType , holder , Derivation . NOT_DERIVED ) ; } }