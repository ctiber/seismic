package client.console.org.apache.syncope.client.console.tasks;

public class NotificationMailBody extends Panel { private static final long serialVersionUID = 3163146190501510888L ; public NotificationMailBody ( final String id , final String body ) { super ( id ) ; add ( new Label ( "body" , Model . of ( body ) ) . setOutputMarkupId ( true ) ) ; } }