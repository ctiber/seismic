package clients.org.apache.kafka.clients.admin;

@ InterfaceStability . Evolving public class ExpireDelegationTokenResult { private final KafkaFuture < Long > expiryTimestamp ; ExpireDelegationTokenResult ( KafkaFuture < Long > expiryTimestamp ) { this . expiryTimestamp = expiryTimestamp ; } public KafkaFuture < Long > expiryTimestamp ( ) { return expiryTimestamp ; } }