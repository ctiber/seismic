package support.guice.org.apache.shiro.guice;

class InitializableInjectionListener < I extends Initializable > implements InjectionListener < I > { public static final Matcher < TypeLiteral > MATCHER = ShiroMatchers . typeLiteral ( Matchers . subclassesOf ( Initializable . class ) ) ; public void afterInjection ( Initializable injectee ) { injectee . init ( ) ; } }