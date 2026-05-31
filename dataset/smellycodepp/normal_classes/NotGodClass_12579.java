package framework.minilang.src.org.ofbiz.minilang.method.entityops;

public static final class RemoveListFactory implements Factory < RemoveList > { @ Override public RemoveList createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new RemoveList ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "remove-list" ; } }