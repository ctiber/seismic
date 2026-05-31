package core.org.apache.struts2.views.velocity.components;

public class OptionTransferSelectDirective extends AbstractDirective { public String getBeanName ( ) { return "optiontransferselect" ; } protected Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new OptionTransferSelect ( stack , req , res ) ; } }