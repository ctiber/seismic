package distribution.release.samples.jax_rs.spring_security.demo.jaxrs.service;

public class SecurityExceptionMapper implements ExceptionMapper < AccessDeniedException > { public Response toResponse ( AccessDeniedException exception ) { return Response . status ( Response . Status . FORBIDDEN ) . build ( ) ; } }