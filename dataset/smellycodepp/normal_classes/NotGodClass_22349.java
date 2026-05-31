package config.ogdl.org.apache.shiro.config.event;

public class DestroyedBeanEvent extends BeanEvent { public DestroyedBeanEvent ( final String beanName , final Object bean , final Map < String , Object > beanContext ) { super ( beanName , bean , beanContext ) ; } }