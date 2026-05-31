package framework.minilang.src.org.ofbiz.minilang.method.envops;

public static final class LoopFactory implements Factory < Loop > { @ Override public Loop createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new Loop ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "loop" ; } }