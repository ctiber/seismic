package core.org.apache.struts2.views.freemarker.tags;

public class ComboBoxModel extends TagModel { public ComboBoxModel ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { super ( stack , req , res ) ; } protected Component getBean ( ) { return new ComboBox ( stack , req , res ) ; } }