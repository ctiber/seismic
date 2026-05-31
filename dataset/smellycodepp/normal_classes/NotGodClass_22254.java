package core.org.apache.shiro.authc.credential;

public class Sha1CredentialsMatcher extends HashedCredentialsMatcher { public Sha1CredentialsMatcher ( ) { super ( ) ; setHashAlgorithmName ( Sha1Hash . ALGORITHM_NAME ) ; } }