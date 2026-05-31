package exec.vector.org.apache.drill.exec.expr.holders;

public class UnionHolder implements ValueHolder { public static final MajorType TYPE = Types . optional ( MinorType . UNION ) ; public FieldReader reader ; public int isSet ; public MajorType getType ( ) { return reader . getType ( ) ; } public boolean isSet ( ) { return isSet == 1 ; } }