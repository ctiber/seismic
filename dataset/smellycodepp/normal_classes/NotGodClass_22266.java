package core.org.apache.shiro.authz.permission;

public class AllPermission implements Permission , Serializable { public boolean implies ( Permission p ) { return true ; } }