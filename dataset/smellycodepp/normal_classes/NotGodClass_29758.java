package core.org.apache.struts2.views.jsp.ui;

public class CheckboxListTag extends AbstractRequiredListTag { private static final long serialVersionUID = 4023034029558150010L ; public Component getBean ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { return new CheckboxList ( stack , req , res ) ; } }