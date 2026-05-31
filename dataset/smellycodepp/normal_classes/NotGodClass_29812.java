package core.org.apache.struts2.views.velocity.components;

public class HiddenDirective extends AbstractDirective { protected Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new Hidden ( stack , req , res ) ; } public String getBeanName ( ) { return "hidden" ; } }