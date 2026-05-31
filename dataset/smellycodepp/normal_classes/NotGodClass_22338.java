package web.org.apache.shiro.web.tags;

public class HasPermissionTag extends PermissionTag { public HasPermissionTag ( ) { } protected boolean showTagBody ( String p ) { return isPermitted ( p ) ; } }