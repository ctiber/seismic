package core.org.apache.shiro.authz.aop;

public class RoleAnnotationMethodInterceptor extends AuthorizingAnnotationMethodInterceptor { public RoleAnnotationMethodInterceptor ( ) { super ( new RoleAnnotationHandler ( ) ) ; } public RoleAnnotationMethodInterceptor ( AnnotationResolver resolver ) { super ( new RoleAnnotationHandler ( ) , resolver ) ; } }