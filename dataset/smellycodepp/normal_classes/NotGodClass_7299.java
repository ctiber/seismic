package core.org.apache.calcite.runtime;

public class RecordEnumeratorCursor < E > extends EnumeratorCursor < E > { private final Class < E > clazz ; public RecordEnumeratorCursor ( Enumerator < E > enumerator , Class < E > clazz ) { super ( enumerator ) ; this . clazz = clazz ; } protected Getter createGetter ( int ordinal ) { return new FieldGetter ( clazz . getFields ( ) [ ordinal ] ) ; } }