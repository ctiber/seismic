package org.apache.commons.math3.analysis.function;

public class Identity implements UnivariateDifferentiableFunction , DifferentiableUnivariateFunction { public double value ( double x ) { return x ; } @ Deprecated public DifferentiableUnivariateFunction derivative ( ) { return new Constant ( 1 ) ; } public DerivativeStructure value ( final DerivativeStructure t ) { return t ; } }