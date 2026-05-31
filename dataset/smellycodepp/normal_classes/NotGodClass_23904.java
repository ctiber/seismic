package tools.corba.org.apache.cxf.tools.corba.common;

public abstract class PrimitiveMapBase { protected Map < String , QName > corbaPrimitiveMap ; public Object get ( Object key ) { return corbaPrimitiveMap . get ( key ) ; } }