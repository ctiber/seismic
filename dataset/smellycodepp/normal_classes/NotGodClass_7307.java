package core.org.apache.calcite.runtime;

private static class DummyTrustManager implements X509TrustManager { public X509Certificate [ ] getAcceptedIssuers ( ) { return null ; } public void checkClientTrusted ( X509Certificate [ ] certs , String authType ) { } public void checkServerTrusted ( X509Certificate [ ] certs , String authType ) { } }