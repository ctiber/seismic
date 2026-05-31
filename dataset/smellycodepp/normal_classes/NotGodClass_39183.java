package core.metamodel.org.apache.isis.core.metamodel.facets.object.wizard;

public abstract class WizardFacetAbstract extends MarkerFacetAbstract implements WizardFacet { public static Class < ? extends Facet > type ( ) { return WizardFacet . class ; } public WizardFacetAbstract ( final FacetHolder holder ) { super ( type ( ) , holder ) ; } }