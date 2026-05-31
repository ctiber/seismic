package src.blocks.forms.org.apache.cocoon.forms.event.impl;

public static class JSCreateListener extends JavaScriptWidgetListener implements CreateListener { public JSCreateListener ( Script script , Context context ) { super ( script , context ) ; } public void widgetCreated ( CreateEvent event ) { super . callScript ( event ) ; } }