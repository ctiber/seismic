package org.apache.commons.collections4.iterators;

public class UniqueFilterIterator < E > extends FilterIterator < E > { public UniqueFilterIterator ( final Iterator < ? extends E > iterator ) { super ( iterator , UniquePredicate . uniquePredicate ( ) ) ; } }