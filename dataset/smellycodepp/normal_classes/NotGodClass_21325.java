package runners.spark.org.apache.beam.runners.spark;

class EmptyListenersList implements DefaultValueFactory < List < JavaStreamingListener > > { @ Override public List < JavaStreamingListener > create ( PipelineOptions options ) { return new ArrayList < > ( ) ; } }