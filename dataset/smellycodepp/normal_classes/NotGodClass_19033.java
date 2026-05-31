package logical.org.apache.drill.common.logical.data;

public static class Builder extends AbstractBuilder < Values > { private JSONOptions content ; public Builder content ( JsonNode n ) { content = new JSONOptions ( n , JsonLocation . NA ) ; return this ; } @ Override public Values build ( ) { return new Values ( content ) ; } }