package src.org.apache.lucene.index;

final static class FieldInvertState { int position ; int length ; int offset ; float boost ; void reset ( float docBoost ) { position = 0 ; length = 0 ; offset = 0 ; boost = docBoost ; } }