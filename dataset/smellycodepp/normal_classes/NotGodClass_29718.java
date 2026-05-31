package core.org.apache.struts2.views.freemarker.tags;

public class DateModel extends TagModel { public DateModel ( ValueStack stack , HttpServletRequest req , HttpServletResponse res ) { super ( stack , req , res ) ; } protected Component getBean ( ) { return new Date ( stack ) ; } }