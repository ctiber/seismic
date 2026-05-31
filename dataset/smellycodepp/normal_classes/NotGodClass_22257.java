package core.org.apache.shiro.authc.credential;

public class Sha512CredentialsMatcher extends HashedCredentialsMatcher { public Sha512CredentialsMatcher ( ) { super ( ) ; setHashAlgorithmName ( Sha512Hash . ALGORITHM_NAME ) ; } }