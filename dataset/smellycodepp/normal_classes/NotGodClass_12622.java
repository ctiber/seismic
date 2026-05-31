package framework.minilang.src.org.ofbiz.minilang.method.ifops;

public static final class IfNotEmptyFactory implements Factory < IfNotEmpty > { @ Override public IfNotEmpty createMethodOperation ( Element element , SimpleMethod simpleMethod ) throws MiniLangException { return new IfNotEmpty ( element , simpleMethod ) ; } @ Override public String getName ( ) { return "if-not-empty" ; } }