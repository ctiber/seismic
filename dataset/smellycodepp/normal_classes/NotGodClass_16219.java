package src.blocks.portal.org.apache.cocoon.portal.pluto.factory;

public class ControllerFactoryImpl extends AbstractFactory implements ControllerFactory { public Controller get ( Model model ) { if ( model instanceof UnmodifiableSet ) { model = ( Model ) ( ( UnmodifiableSet ) model ) . getModifiableSet ( ) ; } return ( Controller ) model ; } }