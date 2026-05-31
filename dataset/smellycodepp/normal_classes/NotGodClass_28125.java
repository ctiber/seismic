package webapp.org.apache.atlas.web.resources;

@ XmlRootElement public static class ErrorBean { public int status ; public String message ; public ErrorBean ( ) { } public ErrorBean ( CatalogException ex ) { this . status = ex . getStatus ( ) ; this . message = ex . getMessage ( ) ; } public int getStatus ( ) { return status ; } public String getMessage ( ) { return message ; } }