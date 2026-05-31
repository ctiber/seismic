package ql.src.org.apache.hadoop.hive.ql.optimizer.ppr;

public class ExprPrunerInfo implements NodeProcessorCtx { String tabAlias ; public String getTabAlias ( ) { return tabAlias ; } public void setTabAlias ( String tabAlias ) { this . tabAlias = tabAlias ; } }