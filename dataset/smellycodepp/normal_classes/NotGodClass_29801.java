package core.org.apache.struts2.views.velocity.components;

public class ActionErrorDirective extends AbstractDirective { public String getBeanName ( ) { return "actionerror" ; } protected Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new ActionError ( stack , req , res ) ; } }