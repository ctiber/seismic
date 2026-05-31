package core.org.apache.struts2.views.freemarker.tags;

public class InputTransferSelectModel extends TagModel { public InputTransferSelectModel ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { super ( stack , req , res ) ; } protected Component getBean ( ) { return new InputTransferSelect ( stack , req , res ) ; } }