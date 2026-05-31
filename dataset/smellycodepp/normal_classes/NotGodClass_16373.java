package src.blocks.woody.org.apache.cocoon.woody.formmodel;

public class NewDefinitionBuilder extends AbstractWidgetDefinitionBuilder { public WidgetDefinition buildWidgetDefinition ( Element element ) throws Exception { NewDefinition definition = new NewDefinition ( ) ; setLocation ( element , definition ) ; setId ( element , definition ) ; return definition ; } }