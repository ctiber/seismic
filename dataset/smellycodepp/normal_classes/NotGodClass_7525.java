package linq4j.org.apache.calcite.linq4j;

public abstract class AbstractEnumerable2 < T > extends DefaultEnumerable < T > { public Enumerator < T > enumerator ( ) { return new Linq4j . IterableEnumerator < > ( this ) ; } }