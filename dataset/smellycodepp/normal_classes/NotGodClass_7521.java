package linq4j.org.apache.calcite.linq4j;

public abstract class AbstractEnumerable < T > extends DefaultEnumerable < T > { public Iterator < T > iterator ( ) { return Linq4j . enumeratorIterator ( enumerator ( ) ) ; } }