package repository.org.apache.atlas.repository;

@ Configuration public class RepositoryConfiguration { @ Bean public GraphDatabase getGraphDatabase ( ) throws IllegalAccessException , InstantiationException { return AtlasRepositoryConfiguration . getGraphDatabaseImpl ( ) . newInstance ( ) ; } @ Bean public TypeSystem getTypeSystem ( ) { return TypeSystem . getInstance ( ) ; } }