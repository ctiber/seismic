package org.apache.commons.io;

static class ForceFileDeleteStrategy extends FileDeleteStrategy { ForceFileDeleteStrategy ( ) { super ( "Force" ) ; } @ Override protected boolean doDelete ( final File fileToDelete ) throws IOException { FileUtils . forceDelete ( fileToDelete ) ; return true ; } }