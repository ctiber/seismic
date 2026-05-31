package src.org.apache.nutch.crawl;

class InlinkPriorityQueue extends PriorityQueue < CrawlDatum > { public InlinkPriorityQueue ( int maxSize ) { initialize ( maxSize ) ; } protected boolean lessThan ( Object arg0 , Object arg1 ) { CrawlDatum candidate = ( CrawlDatum ) arg0 ; CrawlDatum least = ( CrawlDatum ) arg1 ; return candidate . getScore ( ) > least . getScore ( ) ; } }