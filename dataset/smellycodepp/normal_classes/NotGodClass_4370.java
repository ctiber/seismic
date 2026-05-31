package java.org.apache.tomcat.util.bcel.classfile;

public final class ConstantInteger extends Constant { private final int bytes ; ConstantInteger ( DataInput file ) throws IOException { super ( Constants . CONSTANT_Integer ) ; this . bytes = file . readInt ( ) ; } public final int getBytes ( ) { return bytes ; } }