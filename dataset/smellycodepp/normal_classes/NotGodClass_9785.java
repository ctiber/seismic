package ql.src.org.apache.hadoop.hive.ql.udf.generic;

public static class GenericUDAFDenseRankEvaluator extends GenericUDAFRankEvaluator { @ Override protected void nextRank ( RankBuffer rb ) { rb . currentRank ++ ; } }