package src.org.apache.cocoon.matching;

public class WildcardURIMatcher extends AbstractWildcardMatcher { protected String getMatchString ( Map objectModel , Parameters parameters ) { String uri = ObjectModelHelper . getRequest ( objectModel ) . getSitemapURI ( ) ; if ( uri . startsWith ( "/" ) ) { uri = uri . substring ( 1 ) ; } return uri ; } }