#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "types/core.h"

// takes an array of tulip values
// returns `.cons array[0] (.cons array[1] ...)`
tulip_value cons(tulip_value array[], int length) {
  // build `.cons array[n] .nil` tail pair
  tulip_value nil = build_tag("nil", 0, NULL);
  tulip_value tail = build_tag("cons", 2, (tulip_value[]){array[length-1], nil}); //inlining these list constructors seems a little weird but it's working consistently

  // build and nest intermediate pairs
  tulip_value swap = tail;
  for (int i = length-2; 0 < i; i--) {
    swap = build_tag("cons", 2, (tulip_value[]){array[i], swap});
  }

  // build and return head pair
  tulip_value head = build_tag("cons", 2, (tulip_value[]){array[0], swap});
  return head;
}

bool validate_cons(tulip_value subject) { return false; };

// x
// .name "x"
tulip_value name(char* identifier) {
  return build_tag("name", 1, (tulip_value[]){build_string(identifier)});
}

// x/y
// .ns-name (.name x) (.name y)
tulip_value ns_name(char* namespace, char* identifier) {
  return build_tag("ns-name", 2, (tulip_value[]){name(namespace), name(identifier)});
}

// { `statements[1]`; `statements[2]`; ... }
// .block (.cons `statements[1]` (.cons `statements[2]` ...))
tulip_value block(tulip_value statements[], int length){
  return build_tag("block", 1, (tulip_value[]){cons(statements, length)});
}

bool validate_block(){ return false; }

// [ bind => body ]
// .lambda (bind) (body)
tulip_value lambda(tulip_value bind, tulip_value body) {
  return build_tag("lambda", 2, (tulip_value[]){bind, body});
}
bool validate_lambda(){ return false; }

// f x y
// .apply (.name f) (.cons x (.cons y))
tulip_value apply(tulip_value call, tulip_value args[], int saturation){
  return build_tag("apply", 2, (tulip_value[]){call, cons(args, saturation)});
}
bool validate_apply(){ return false; }

// bind = definition
// .let (bind) (definition)
tulip_value let(tulip_value bind, tulip_value definition){
  return build_tag("let", 2, (tulip_value[]){bind, definition});
}
bool validate_let(){ return false; }

// println/1 x
// .builtin "println" 1 (.cons (.name x) nil)
tulip_value builtin(char* builtin_name, int arity, tulip_value args[], int saturation) {
  return build_tag("builting", 3, (tulip_value[]){build_string(builtin_name), build_number(arity), cons(args, saturation)});
}

bool validate_builtin(){ return false; }

// takes two lists of tulip values (same length) as predicate/consequence pairs
// returns `.branch (.cons ...) (.cons ...)`
tulip_value branch(tulip_value predicates[], tulip_value consequences[], int length) {
  return build_tag("branch", 2, (tulip_value[]){cons(predicates, length), cons(consequences, length)});
}
bool validate_branch(){ return false; }
