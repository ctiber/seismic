package bulkloader.org.apache.directory.mavibot.btree;

@ SuppressWarnings ( "all" ) public class IndexTupleComparator implements Comparator < Tuple > { private Comparator keyComp ; public IndexTupleComparator ( Comparator keyComp ) { this . keyComp = keyComp ; } @ Override public int compare ( Tuple o1 , Tuple o2 ) { return keyComp . compare ( o1 . getKey ( ) , o2 . getKey ( ) ) ; } }