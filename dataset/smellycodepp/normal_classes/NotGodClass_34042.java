package plugins.openldap.config.editor.org.apache.directory.studio.openldap.config.model.database;

public class OlcShellConfig extends OlcDatabaseConfig { @ Override public String getOlcDatabaseType ( ) { return DatabaseTypeEnum . SHELL . toString ( ) . toLowerCase ( ) ; } }