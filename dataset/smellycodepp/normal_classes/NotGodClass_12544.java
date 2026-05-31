package framework.minilang.src.org.ofbiz.minilang.method.callops;

public static final class CallBshFactory implements Factory < CallBsh > { @ Override public CallBsh createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new CallBsh ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "call-bsh" ; } }