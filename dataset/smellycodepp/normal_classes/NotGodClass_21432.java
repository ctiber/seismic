package sdks.core.org.apache.beam.sdk.values;

public static class StripIdsDoFn < T > extends DoFn < ValueWithRecordId < T > , T > { @ ProcessElement public void processElement ( ProcessContext c ) { c . output ( c . element ( ) . getValue ( ) ) ; } }