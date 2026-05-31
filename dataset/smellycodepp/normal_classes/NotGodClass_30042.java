package org.apache.commons.lang3.text;

static final class TrimMatcher extends StrMatcher { TrimMatcher ( ) { super ( ) ; } @ Override public int isMatch ( final char [ ] buffer , final int pos , final int bufferStart , final int bufferEnd ) { return buffer [ pos ] <= 32 ? 1 : 0 ; } }