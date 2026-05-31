package core.org.apache.calcite.interpreter;

public class MatchNode extends AbstractSingleNode < Match > { MatchNode ( Compiler compiler , Match rel ) { super ( compiler , rel ) ; } public void run ( ) throws InterruptedException { Row row ; while ( ( row = source . receive ( ) ) != null ) { sink . send ( row ) ; } sink . end ( ) ; } }