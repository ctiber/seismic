package logical.org.apache.drill.common.logical.data;

public static class Builder extends AbstractSingleBuilder < Writer , Builder > { private Object createTableEntry ; public Builder setCreateTableEntry ( Object createTableEntry ) { this . createTableEntry = createTableEntry ; return this ; } @ Override public Writer internalBuild ( ) { return new Writer ( createTableEntry ) ; } }