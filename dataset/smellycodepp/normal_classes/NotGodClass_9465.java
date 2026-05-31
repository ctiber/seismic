package ql.src.org.apache.hadoop.hive.ql.exec.vector.expressions;

public class VectorUDFDateSubColCol extends VectorUDFDateAddColCol { public VectorUDFDateSubColCol ( int colNum1 , int colNum2 , int outputColumn ) { super ( colNum1 , colNum2 , outputColumn ) ; isPositive = false ; } public VectorUDFDateSubColCol ( ) { super ( ) ; isPositive = false ; } }