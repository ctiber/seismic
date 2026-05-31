package sdks.extensions.sql.org.apache.beam.sdk.extensions.sql.impl.interpreter.operator.arithmetic;

public class BeamSqlMultiplyExpression extends BeamSqlArithmeticExpression { public BeamSqlMultiplyExpression ( List < BeamSqlExpression > operands ) { super ( operands ) ; } @ Override protected BigDecimal calc ( BigDecimal left , BigDecimal right ) { return left . multiply ( right ) ; } }