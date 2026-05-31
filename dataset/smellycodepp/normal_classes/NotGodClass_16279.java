package src.org.apache.cocoon.selection;

public class RequestMethodSelector extends AbstractLogEnabled implements ThreadSafe , Selector { public boolean select ( String expression , Map objectModel , Parameters parameters ) { String method = ObjectModelHelper . getRequest ( objectModel ) . getMethod ( ) ; return method . equals ( expression ) ; } }