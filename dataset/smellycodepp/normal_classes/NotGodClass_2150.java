package core.org.apache.accumulo.core.cli;

public class BatchScannerOpts { @ Parameter ( names = "--scanThreads" , description = "Number of threads to use when batch scanning" ) public Integer scanThreads = 10 ; @ Parameter ( names = "--scanTimeout" , converter = TimeConverter . class , description = "timeout used to fail a batch scan" ) public Long scanTimeout = Long . MAX_VALUE ; }