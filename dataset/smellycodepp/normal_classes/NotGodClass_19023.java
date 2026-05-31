package logical.org.apache.drill.common.logical;

public class UnexpectedOperatorType extends ValidationError { public UnexpectedOperatorType ( String message ) { super ( message ) ; } public UnexpectedOperatorType ( Object operator , String message ) { super ( message + " Received node of type " + operator . getClass ( ) . getCanonicalName ( ) ) ; } }