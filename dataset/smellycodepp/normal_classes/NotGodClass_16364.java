package src.blocks.woody.org.apache.cocoon.woody.flowscript;

public class WoodyFlowHelper { private WoodyFlowHelper ( ) { } public static final FormContext getFormContext ( FOM_Cocoon cocoon , Locale locale ) { return new FormContext ( cocoon . getRequest ( ) , locale ) ; } }