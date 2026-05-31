package core.org.apache.accumulo.core.data;

@ Deprecated public class ComparableBytes extends BinaryComparable { public byte [ ] data ; public ComparableBytes ( byte [ ] b ) { this . data = b ; } @ Override public byte [ ] getBytes ( ) { return data ; } @ Override public int getLength ( ) { return data . length ; } }