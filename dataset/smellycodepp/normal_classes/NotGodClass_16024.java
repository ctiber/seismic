package src.org.apache.cocoon.acting;

public abstract class ConfigurableComposerAction extends AbstractConfigurableAction implements Composable { protected ComponentManager manager ; public void compose ( ComponentManager manager ) throws ComponentException { this . manager = manager ; } }