package api.org.apache.cxf.configuration.jsse;

public class TLSServerParameters extends TLSParameterBase { ClientAuthentication clientAuthentication ; public final void setClientAuthentication ( ClientAuthentication clientAuth ) { clientAuthentication = clientAuth ; } public ClientAuthentication getClientAuthentication ( ) { return clientAuthentication ; } }