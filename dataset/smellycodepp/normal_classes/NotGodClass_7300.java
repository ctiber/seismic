package core.org.apache.calcite.runtime;

public class Unit implements Comparable < Unit > { public static final Unit INSTANCE = new Unit ( ) ; private Unit ( ) { } public int compareTo ( Unit that ) { return 0 ; } public String toString ( ) { return "{}" ; } }