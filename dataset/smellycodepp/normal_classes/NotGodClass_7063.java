package core.org.apache.calcite.model;

public class JsonColumn { public String name ; public void accept ( ModelHandler handler ) { handler . visit ( this ) ; } }