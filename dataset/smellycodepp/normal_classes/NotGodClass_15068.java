package clients.org.apache.kafka.common.serialization;

public class ByteBufferDeserializer implements Deserializer < ByteBuffer > { public ByteBuffer deserialize ( String topic , byte [ ] data ) { if ( data == null ) return null ; return ByteBuffer . wrap ( data ) ; } }