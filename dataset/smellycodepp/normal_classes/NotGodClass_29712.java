package core.org.apache.struts2.views.freemarker.tags;

public class AnchorModel extends TagModel { public AnchorModel ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { super ( stack , req , res ) ; } protected Component getBean ( ) { return new Anchor ( stack , req , res ) ; } }