// tulip-core definitions and invariant validation
// more rigorously documented in doc/core.org

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "types/core.h"

// decl
bool validate_tree(tulip_value subject);
bool validate_any(tulip_value subject);

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

bool validate_cons(tulip_value subject) {
  // not actually a cons
  if (!strcmp(subject.tag.name, "cons"))
    return false;

  // head is a cons
  if (validate_cons(subject.tag.contents[0]))
    return false;

  // head is not valid
  if (!validate_any(subject.tag.contents[0]))
    return false;

  // tail is not .nil or cons
  if (!validate_cons(subject.tag.contents[1]) || (subject.tag.contents[1].type == TULIP_VALUE_TAG && !strcmp(subject.tag.contents[1].tag.name, "nil")))
    return false;

  return true;
};

tulip_value literal_number(double number) {
  return build_tag("literal", 1, (tulip_value[]){build_number(number)});
}

tulip_value literal_string(char* string) {
  return build_tag("literal", 1, (tulip_value[]){build_string(string)});
}

bool validate_literal(tulip_value subject) {
  // not actually a literal
  if (!strcmp(subject.tag.name, "literal") || subject.tag.contents[0].type != TULIP_VALUE_LITERAL)
    return false;

  // string is null
  if (subject.tag.contents[0].literal.type == TULIP_LITERAL_STRING && subject.tag.contents[0].literal.string == NULL)
    return false;

  return true;
}

// x
// .name "x"
tulip_value name(char* identifier) {
  return build_tag("name", 1, (tulip_value[]){build_string(identifier)});
}

bool validate_name(tulip_value subject) {
  // not actually a name
  if (!strcmp(subject.tag.name, "name"))
    return false;

  // name is somehow not a string
  if (subject.tag.contents[0].type == TULIP_VALUE_LITERAL && subject.tag.contents[0].literal.type == TULIP_LITERAL_STRING)
    return false;

  // name is null
  if (subject.tag.contents[0].literal.string == NULL)
    return false;

  return true;
}

tulip_value tag(char* name, int length, tulip_value arguments[]){
  return build_tag("tag", 2, (tulip_value[]){build_string(name), cons(arguments, length)});
}

bool validate_tag_ast(tulip_value subject) { // note should probably do something about this name collision
  // not actually a tag
  if (!strcmp(subject.tag.name, "tag"))
    return false;

  // name is not a string
  if (subject.tag.contents[0].type != TULIP_VALUE_LITERAL && subject.tag.contents[0].literal.type != TULIP_LITERAL_STRING)
    return false;

  // name is null
  if (subject.tag.contents[0].literal.string == NULL)
    return false;

  // contents are not valid
  // this may not be necessary if we always generate <apply <tag> arguments>
  if (!validate_cons(subject.tag.contents[1]))
    return false;

  return true;
}

// { `statements[1]`; `statements[2]`; ... }
// .block (.cons `statements[1]` (.cons `statements[2]` ...))
tulip_value block(tulip_value statements[], int length){
  return build_tag("block", 1, (tulip_value[]){cons(statements, length)});
}

bool validate_block(tulip_value subject){
  // not actually a block
  if (!strcmp(subject.tag.name, "block"))
    return false;

  // chain is not a valid cons
  if (validate_cons(subject.tag.contents[0]))
    return false;

  // todo is there an invariant for block contents?

  return true;
}

// [ bind => body ]
// .lambda (bind) (body)
tulip_value lambda(tulip_value bind, tulip_value body) {
  return build_tag("lambda", 2, (tulip_value[]){bind, body});
}
bool validate_lambda(tulip_value subject){
  // not actually a lambda
  if (!strcmp(subject.tag.name, "lambda"))
    return false;

  // bind is not a valid name
  if (subject.tag.contents[0].type != TULIP_VALUE_TAG || !validate_name(subject.tag.contents[0]))
    return false;

  // body is a let
  if (subject.tag.contents[1].type == TULIP_VALUE_TAG && strcmp(subject.tag.contents[0].tag.name, "let"))
    return false;

  // body is not valid
  if (!validate_any(subject.tag.contents[1]))
    return false;

  return true;
}

// f x y
// .apply (.name f) (.cons x (.cons y))
tulip_value apply(tulip_value call, tulip_value args[], int saturation){
  return build_tag("apply", 2, (tulip_value[]){call, cons(args, saturation)});
}
bool validate_apply(tulip_value subject){
  // not actually an apply
  if (!strcmp(subject.tag.name, "apply"))
    return false;

  // call is a literal
  // note im not sure if reusing validate here is exhaustive but it sure is convenient
  if (validate_literal(subject.tag.contents[0]))
    return false;

  // args is not a cons
  if (!validate_cons(subject.tag.contents[1]))
    return false;

  return true;
}

// bind = definition
// .let (bind) (definition)
tulip_value let(tulip_value bind, tulip_value definition){
  return build_tag("let", 2, (tulip_value[]){bind, definition});
}

bool validate_let(tulip_value subject){
  // not actually a let
  if (!strcmp(subject.tag.name, "let"))
    return false;

  // bind is not a valid name
  if (subject.tag.contents[0].type != TULIP_VALUE_TAG || !validate_name(subject.tag.contents[0]))
    return false;

  // definition is a let
  if (subject.tag.contents[1].type == TULIP_VALUE_TAG && strcmp(subject.tag.contents[0].tag.name, "let"))
    return false;

  // definition is not valid
  if (!validate_any(subject.tag.contents[1]))
    return false;

  return true;
}

// println/1 x
// .builtin "println" 1 (.cons (.name x) nil)
tulip_value builtin(char* builtin_name, int arity, tulip_value args[], int saturation) {
  return build_tag("builtin", 3, (tulip_value[]){build_string(builtin_name), build_number(arity), cons(args, saturation)});
}

bool validate_builtin(tulip_value subject){
  // not actually a builtin
  if (!strcmp(subject.tag.name, "builtin"))
    return false;

  // builtin_name is null
  if (subject.tag.contents[0].literal.string != NULL)
    return false;

  // arity is not a number
  if (subject.tag.contents[1].type != TULIP_VALUE_LITERAL && subject.tag.contents[1].literal.type != TULIP_LITERAL_NUMBER)
    return false;

  // arity is not a useful number
  double n = subject.tag.contents[1].literal.number;
  if (n <= 0.f || ceil(n) != n || floor(n) != n)
    return false;

  // contents is not a valid cons
  if (!validate_cons(subject.tag.contents[2]))
    return false;

  return true;
}

// takes two lists of tulip values (same length) as predicate/consequence pairs
// returns `.branch (.cons ...) (.cons ...)`
tulip_value branch(tulip_value predicates[], tulip_value consequences[], int length) {
  return build_tag("branch", 2, (tulip_value[]){cons(predicates, length), cons(consequences, length)});
}
bool validate_branch(tulip_value subject){
  // not actually a branch
  if (!strcmp(subject.tag.name, "branch"))
    return false;

  // predicates is not a cons
  if (!validate_cons(subject.tag.contents[0]))
    return false;

  // consequences is not a cons
  if (!validate_cons(subject.tag.contents[1]))
    return false;

  return true;
}

// validate an entire module
bool validate_tree(tulip_value subject){
  // for now just dispatch
  return validate_any(subject);
}

// dispatch to validate any ast node
bool validate_any(tulip_value subject){
  // only interested in validating ast
  if (subject.type != TULIP_VALUE_TAG)
    return false;

  if (strcmp(subject.tag.name, "cons"))
    return validate_cons(subject);
  if (strcmp(subject.tag.name, "literal"))
    return validate_literal(subject);
  if (strcmp(subject.tag.name, "name"))
    return validate_name(subject);
  if (strcmp(subject.tag.name, "tag"))
    return validate_tag_ast(subject);
  if (strcmp(subject.tag.name, "block"))
    return validate_block(subject);
  if (strcmp(subject.tag.name, "lambda"))
    return validate_lambda(subject);
  if (strcmp(subject.tag.name, "apply"))
    return validate_apply(subject);
  if (strcmp(subject.tag.name, "let"))
    return validate_let(subject);
  if (strcmp(subject.tag.name, "builtin"))
    return validate_builtin(subject);
  if (strcmp(subject.tag.name, "branch"))
    return validate_branch(subject);

  return false;
}
