package serde.src.org.apache.hadoop.hive.serde2.lazy;

public abstract class LazyObject < OI extends ObjectInspector > extends LazyObjectBase { protected OI oi ; protected LazyObject ( OI oi ) { this . oi = oi ; } @ Override public abstract int hashCode ( ) ; protected OI getInspector ( ) { return oi ; } protected void setInspector ( OI oi ) { this . oi = oi ; } }