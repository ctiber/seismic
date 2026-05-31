package core.org.apache.struts2.views.velocity.components;

public class HeadDirective extends AbstractDirective { protected Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new Head ( stack , req , res ) ; } public String getBeanName ( ) { return "head" ; } }