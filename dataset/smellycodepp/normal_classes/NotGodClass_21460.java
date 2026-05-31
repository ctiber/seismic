package sdks.extensions.sql.org.apache.beam.sdk.extensions.sql.impl.interpreter.operator.arithmetic;

public class BeamSqlMinusExpression extends BeamSqlArithmeticExpression { public BeamSqlMinusExpression ( List < BeamSqlExpression > operands ) { super ( operands ) ; } @ Override protected BigDecimal calc ( BigDecimal left , BigDecimal right ) { return left . subtract ( right ) ; } }