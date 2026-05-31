package framework.common.src.org.ofbiz.common.scripting;

public final class ScriptHelperFactoryImpl implements ScriptHelperFactory { @ Override public ScriptHelper getInstance ( ScriptContext context ) { return new ScriptHelperImpl ( context ) ; } }