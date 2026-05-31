package core.metamodel.org.apache.isis.objectstore.jdo.metamodel.facets.prop.column;

public class MandatoryFacetInferredFromAbsenceOfJdoColumn extends MandatoryFacetAbstract { public MandatoryFacetInferredFromAbsenceOfJdoColumn ( final FacetHolder holder , final boolean required ) { super ( holder , Semantics . of ( required ) ) ; } }