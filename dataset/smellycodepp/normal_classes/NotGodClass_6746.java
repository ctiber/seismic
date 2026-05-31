package src.org.apache.nutch.crawl;

public class TextMD5Signature extends Signature { Signature fallback = new MD5Signature ( ) ; public byte [ ] calculate ( Content content , Parse parse ) { String text = parse . getText ( ) ; if ( text == null || text . length ( ) == 0 ) { return fallback . calculate ( content , parse ) ; } return MD5Hash . digest ( text ) . getDigest ( ) ; } }