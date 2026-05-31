package apps.mailreader.mailreader2;

public final class Login extends MailreaderSupport { public String execute ( ) throws ExpiredPasswordException { User user = findUser ( getUsername ( ) , getPassword ( ) ) ; if ( user != null ) { setUser ( user ) ; } if ( hasErrors ( ) ) { return INPUT ; } return SUCCESS ; } }