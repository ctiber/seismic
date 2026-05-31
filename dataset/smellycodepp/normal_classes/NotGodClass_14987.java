package clients.org.apache.kafka.common.metrics.stats;

private static class HistogramSample extends SampledStat . Sample { private final Histogram histogram ; private HistogramSample ( BinScheme scheme , long now ) { super ( 0.0 , now ) ; this . histogram = new Histogram ( scheme ) ; } @ Override public void reset ( long now ) { super . reset ( now ) ; this . histogram . clear ( ) ; } }