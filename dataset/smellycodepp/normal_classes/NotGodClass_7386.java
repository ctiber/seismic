package core.org.apache.calcite.sql.fun;

@ Deprecated class SqlGroupingIdFunction extends SqlAbstractGroupFunction { SqlGroupingIdFunction ( ) { super ( "GROUPING_ID" , SqlKind . GROUPING_ID , ReturnTypes . BIGINT , null , OperandTypes . ONE_OR_MORE , SqlFunctionCategory . SYSTEM ) ; } }