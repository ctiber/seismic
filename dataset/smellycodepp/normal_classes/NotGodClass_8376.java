package livy.org.apache.zeppelin.livy;

public class LivyPySparkInterpreter extends LivyPySparkBaseInterpreter { public LivyPySparkInterpreter ( Properties property ) { super ( property ) ; } @ Override public String getSessionKind ( ) { return "pyspark" ; } }