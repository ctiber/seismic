package framework.minilang.src.org.ofbiz.minilang.method.envops;

public static final class WhileFactory implements Factory < While > { @ Override public While createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new While ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "while" ; } }