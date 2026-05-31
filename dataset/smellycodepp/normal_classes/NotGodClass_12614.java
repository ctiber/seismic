package framework.minilang.src.org.ofbiz.minilang.method.envops;

public static final class ToStringFactory implements Factory < ToString > { @ Override public ToString createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new ToString ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "to-string" ; } }