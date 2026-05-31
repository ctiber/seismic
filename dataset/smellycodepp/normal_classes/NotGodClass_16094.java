package src.org.apache.cocoon.components;

final class CloningInheritableThreadLocal extends InheritableThreadLocal { protected Object childValue ( Object parentValue ) { if ( null != parentValue ) { return ( ( EnvironmentStack ) parentValue ) . clone ( ) ; } else { return null ; } } }