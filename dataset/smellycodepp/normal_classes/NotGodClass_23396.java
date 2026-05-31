package distribution.release.samples_first_pojo.demo.hw.server;

public class HelloWorldImpl implements HelloWorld { public String sayHi ( String text ) { System . out . println ( "sayHi called" ) ; return "Hello " + text ; } }