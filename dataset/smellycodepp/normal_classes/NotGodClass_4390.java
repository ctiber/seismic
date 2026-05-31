package java.org.apache.tomcat.util.http.fileupload;

static class ForceFileDeleteStrategy extends FileDeleteStrategy { ForceFileDeleteStrategy ( ) { super ( "Force" ) ; } @ Override protected boolean doDelete ( File fileToDelete ) throws IOException { FileUtils . forceDelete ( fileToDelete ) ; return true ; } }