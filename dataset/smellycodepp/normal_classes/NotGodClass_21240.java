package runners.direct.org.apache.beam.runners.direct.portable.job;

private static class ServerConfiguration { @ Option ( name = "-p" , aliases = { "--port" } , usage = "The local port to expose the server on. 0 to use a dynamic port. (Default: 8099)" ) private int port = 8099 ; }