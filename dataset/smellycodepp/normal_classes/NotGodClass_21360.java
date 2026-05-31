package sdks.core.org.apache.beam.sdk.options;

class AtomicLongFactory implements DefaultValueFactory < Long > { private static final AtomicLong NEXT_ID = new AtomicLong ( 0 ) ; @ Override public Long create ( PipelineOptions options ) { return NEXT_ID . getAndIncrement ( ) ; } }