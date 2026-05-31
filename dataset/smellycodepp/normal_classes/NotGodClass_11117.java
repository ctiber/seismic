package core.org.apache.carbondata.core.metadata.datatype;

class IntType extends DataType { static final DataType INT = new IntType ( DataTypes . INT_TYPE_ID , 3 , "INT" , 4 ) ; private IntType ( int id , int precedenceOrder , String name , int sizeInBytes ) { super ( id , precedenceOrder , name , sizeInBytes ) ; } private Object readResolve ( ) { return DataTypes . INT ; } }