package rt.bindings.corba.org.apache.cxf.binding.corba.types;

public class CorbaFixedListener extends AbstractCorbaTypeListener { public CorbaFixedListener ( CorbaObjectHandler handler ) { super ( handler ) ; } public void processCharacters ( String text ) { ( ( CorbaFixedHandler ) handler ) . setValueFromData ( text ) ; } }