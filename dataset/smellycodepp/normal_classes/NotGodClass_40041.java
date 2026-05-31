package contrib.swing.src.org.apache.lucene.swing.models;

private class TableModelHandler implements TableModelListener { public void tableChanged ( TableModelEvent e ) { if ( ! isSearching ( ) ) { clearSearchingState ( ) ; reindex ( ) ; fireTableChanged ( e ) ; return ; } reindex ( ) ; search ( searchString ) ; fireTableDataChanged ( ) ; return ; } }