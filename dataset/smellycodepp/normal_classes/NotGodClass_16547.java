package src.org.apache.cocoon.components.treeprocessor;

public class ContainerNode extends SimpleParentProcessingNode { public final boolean invoke ( Environment env , InvokeContext context ) throws Exception { return invokeNodes ( this . children , env , context ) ; } }