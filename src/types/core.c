#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "types/core.h"

// takes an array of tulip values
// returns `.cons array[0] (.cons array[1] ...)`
// temporarily reduced to only the tail pair `.cons array[n-1] .nil` because i'm having some trouble with it
tulip_value_t* cons(tulip_value_t* array, int length) {
  tulip_value_t* nil = (tulip_value_t*) build_tag("nil", 0, NULL);
  printf("%s\n", nil->tag->tag_name);
  tulip_value_t* tail_c = malloc(2*sizeof(tulip_value_t));

  tulip_value_t tail_a[] = { array[length-1], *nil };

  memcpy(tail_c, tail_a, 2*sizeof(tulip_value_t));

  printf("tail value: %s\n", tail_c[0].literal_string);

  tulip_value_t* tail = (tulip_value_t*) build_tag("cons", 2, tail_c);

  return tail;
}

bool validate_cons(tulip_value_t* subject) { return false; };

// takes a list of tulip values as block statements
// returns `.block (.cons ...)`
tulip_value_t* block(tulip_value_t* statements, int length){
  // this malloc seems extraneous
  tulip_value_t* statements_ = malloc(sizeof(tulip_value_t));
  tulip_value_t* statements_c = cons(statements, length);

  // also this _might_ be nonsensical
  // i dont fully understand heap semantics yet
  memcpy(statements_, (tulip_value_t []) {*statements_c}, sizeof(tulip_value_t));

  tulip_value_t* block_tag = (tulip_value_t*) build_tag("block", 1, statements_);
  return block_tag;
}

bool validate_block(tulip_value_t* subject){
  return false;
}

tulip_value_t* lambda(){ return NULL; }
bool validate_lambda(){ return false; }
tulip_value_t* apply(){ return NULL; }
bool validate_apply(){ return false; }
tulip_value_t* let(){ return NULL; }
bool validate_let(){ return false; }
tulip_value_t* builtin(){ return NULL; }
bool validate_builtin(){ return false; }

// takes two lists of tulip values (same length) as predicate/consequence pairs
// returns `.branch (.cons ...) (.cons ...)`
tulip_value_t* branch(tulip_value_t* predicates, tulip_value_t* consequences, int length) {
  // yeah this could/should be a lot prettier
  tulip_value_t* predicates_c = cons(predicates, length);
  tulip_value_t* consequences_c = cons(predicates, length);

  tulip_value_t* contents = malloc(sizeof(tulip_value_t) * 2);
  memcpy(contents, (tulip_value_t []) {*predicates_c, *consequences_c}, sizeof(tulip_value_t)*2);

  tulip_value_t* branch_tag = (tulip_value_t*) build_tag("branch", 2, contents);

  return branch_tag;
}
bool validate_branch(){ return false; }
