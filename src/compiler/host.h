#pragma once

#include <stdbool.h>
#include <lua.h>
#include "types/value.h"

// character reader
// TODO move out to proper file handling

typedef struct char_reader_state {
  int index;
  char* input;
  int length;
} char_reader_state;

char_reader_state* char_reader_setup();
void char_reader_teardown(char_reader_state* state);
char char_reader_next(char_reader_state* state);

tulip_value compiler_create_tag(char* name, int length, tulip_value* values);
tulip_value compiler_tag_get(tulip_value tag, unsigned int index);
bool compiler_matches_tag(tulip_value tag, char* name, int arity);
char* compiler_inspect_value(tulip_value value);

typedef struct tulip_compiler_state {
  lua_State* lua_state;
} tulip_compiler_state;

tulip_compiler_state* tulip_compiler_start();
void tulip_compiler_stop();
