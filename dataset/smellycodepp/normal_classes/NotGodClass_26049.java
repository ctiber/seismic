package org.apache.commons.math3.optimization;

@ Deprecated public class Target implements OptimizationData { private final double [ ] target ; public Target ( double [ ] observations ) { target = observations . clone ( ) ; } public double [ ] getTarget ( ) { return target . clone ( ) ; } }