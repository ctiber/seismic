package testutils.org.apache.hello_world_doc_lit;

@ WebService ( serviceName = "MultiTransportService" , portName = "JMSPort" , endpointInterface = "org.apache.hello_world_doc_lit.Greeter" , targetNamespace = "http://apache.org/hello_world_doc_lit" , wsdlLocation = "testutils/hello_world_doc_lit.wsdl" ) public class JMSGreeterImpl extends MultiTransportGreeter { }