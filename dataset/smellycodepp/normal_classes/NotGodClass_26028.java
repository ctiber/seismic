package org.apache.commons.math3.ode;

public class UnknownParameterException extends MathIllegalArgumentException { private static final long serialVersionUID = 20120902L ; private final String name ; public UnknownParameterException ( final String name ) { super ( LocalizedFormats . UNKNOWN_PARAMETER ) ; this . name = name ; } public String getName ( ) { return name ; } }