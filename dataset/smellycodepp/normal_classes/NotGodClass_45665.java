package org.apache.commons.cli;

private static class OptionComparator implements Comparator < Option > , Serializable { private static final long serialVersionUID = 5305467873966684014L ; public int compare ( Option opt1 , Option opt2 ) { return opt1 . getKey ( ) . compareToIgnoreCase ( opt2 . getKey ( ) ) ; } }