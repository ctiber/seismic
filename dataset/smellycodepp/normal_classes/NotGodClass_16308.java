package src.blocks.taglib.org.apache.cocoon.taglib;

public abstract class VarXMLProducerTagSupport extends VarTagSupport implements XMLProducerTag { protected XMLConsumer xmlConsumer ; public void setConsumer ( XMLConsumer xmlConsumer ) { this . xmlConsumer = xmlConsumer ; } public void recycle ( ) { xmlConsumer = null ; super . recycle ( ) ; } }