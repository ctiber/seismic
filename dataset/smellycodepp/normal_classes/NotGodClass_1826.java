package bundle.core.org.apache.karaf.bundle.command;

@ Command ( scope = "bundle" , name = "id" , description = "Gets the bundle ID." ) @ Service public class Id extends BundleCommand { @ Override protected Object doExecute ( Bundle bundle ) throws Exception { System . out . println ( bundle . getBundleId ( ) ) ; return null ; } }