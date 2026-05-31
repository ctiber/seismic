package sdks.testing.nexmark.org.apache.beam.sdk.nexmark.sources.generator.model;

public class LongGenerator { public static long nextLong ( Random random , long n ) { if ( n < Integer . MAX_VALUE ) { return random . nextInt ( ( int ) n ) ; } else { return Math . abs ( random . nextLong ( ) % n ) ; } } }