package framework.minilang.src.org.ofbiz.minilang.method.envops;

public static final class IterateMapFactory implements Factory < IterateMap > { @ Override public IterateMap createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new IterateMap ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "iterate-map" ; } }