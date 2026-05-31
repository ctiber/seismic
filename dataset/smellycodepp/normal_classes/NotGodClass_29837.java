package plugins.dojo.org.apache.struts2.dojo.views.velocity.components;

public class HeadDirective extends DojoAbstractDirective { protected Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new Head ( stack , req , res ) ; } public String getBeanName ( ) { return "head" ; } }