#include <stdlib.h>
#include <lauxlib.h>
#include <lualib.h>
#include <string.h>

#include "compiler/host.h"
#include "types/value.h"

char_reader_state* char_reader_setup(char* input, int length) {
  char_reader_state* state = malloc(sizeof(char_reader_state));
  state->index  = 0;
  state->input  = input;
  state->length = length;
  return state;
}

int Lchar_reader_setup(lua_State* s) {
  char* input = lua_tostring(s, 1);
  int length = lua_tointeger(s, 2);

  lua_pushlightuserdata(s, char_reader_setup(input, length));
  return 1;
}

void char_reader_teardown(char_reader_state* state) {
  free(state);
}

int Lchar_reader_teardown(lua_State* s) {
  char_reader_state* state = lua_topointer(s, 1);

  char_reader_teardown(state);

  return 0;
}

char char_reader_next(char_reader_state* state) {
  if(state->index < state->length) {
    char v = state->input[state->index];
    state->index = state->index + 1;
    return v;
  } else { return (char) NULL; }
}

int Lchar_reader_next(lua_State* s) {
  char_reader_state* state = lua_topointer(s, 1);
  char* b = "\0";

  b[0] = char_reader_next(state);

  lua_pushstring(s, b);
  return 1;
}

tulip_value compiler_create_tag(char* name, int length, tulip_value* values) {
  return build_tag(name, length, values);
}

int Lcompiler_create_tag(lua_State* s) {
  char* name = lua_tostring(s, 1);
  int length = lua_tointeger(s, 2);
  tulip_value** values = (tulip_value**) lua_topointer(s, 3);

  // [pretty] this is an awful workaround and can be avoided
  tulip_value* value = malloc(sizeof(tulip_value));
  tulip_value f = compiler_create_tag(name, length, *values);
  memcpy(value, &f, sizeof(tulip_value));

  lua_pushlightuserdata(s, value);
  return 1;
}

tulip_value compiler_tag_get(tulip_value tag, unsigned int index) {
  if (tag.type != TULIP_VALUE_TAG) return build_tag("nil", 0, NULL);

  if (index < tag.tag.length) {
    return tag.tag.contents[index];
  } else {
    return build_tag("nil", 0, NULL);
  }
}

int Lcompiler_tag_get(lua_State* s) {
  tulip_value* tag = (tulip_value*) lua_topointer(s, 1);
  unsigned int index = lua_tointeger(s, 2);

  // [pretty] this is an awful workaround and can be avoided
  tulip_value* value = malloc(sizeof(tulip_value));
  tulip_value f = compiler_tag_get(*tag, index);
  memcpy(value, &f, sizeof(tulip_value));

  lua_pushlightuserdata(s, value);
  return 1;
}

bool compiler_matches_tag(tulip_value tag, char* name, int arity) {
  return (tag.type == TULIP_VALUE_TAG && tag.tag.name == name && tag.tag.length == (unsigned int) arity);
}

int Lcompiler_matches_tag(lua_State* s) {
  tulip_value* tag = (tulip_value*) lua_topointer(s, 1);
  char* name = lua_tostring(s, 2);
  int arity = lua_tointeger(s, 3);

  lua_pushboolean(s, compiler_matches_tag(*tag, name, arity));
  return 1;
}

char* compiler_inspect_value(tulip_value value) {
  // [recheck] does printing values need to be specialized for the compiler?
  return show_value(value);
}

int Lcompiler_inspect_value(lua_State* s) {
  tulip_value* value = (tulip_value*) lua_topointer(s, 1);

  lua_pushstring(s, compiler_inspect_value(*value));
  return 1;
}

tulip_compiler_state* tulip_compiler_start() {
  tulip_compiler_state* state = malloc(sizeof(tulip_compiler_state));

  state->lua_state = luaL_newstate();
  luaL_openlibs(state->lua_state);

  // wrap and inject the utility functions defined above
  lua_pushcfunction(state->lua_state, Lchar_reader_setup);
  lua_setglobal(state->lua_state, "__compiler_reader_setup");
  lua_pushcfunction(state->lua_state, Lchar_reader_teardown);
  lua_setglobal(state->lua_state, "__compiler_reader_teardown");
  lua_pushcfunction(state->lua_state, Lchar_reader_next);
  lua_setglobal(state->lua_state, "__compiler_reader_next");

  lua_pushcfunction(state->lua_state, Lcompiler_create_tag);
  lua_setglobal(state->lua_state, "__compiler_create_tag");
  lua_pushcfunction(state->lua_state, Lcompiler_tag_get);
  lua_setglobal(state->lua_state, "__compiler_tag_get");
  lua_pushcfunction(state->lua_state, Lcompiler_matches_tag);
  lua_setglobal(state->lua_state, "__compiler_matches_tag");
  lua_pushcfunction(state->lua_state, Lcompiler_inspect_value);
  lua_setglobal(state->lua_state, "__compiler_inspect_value");

  // [todo] better loading of lua sources
  if (luaL_dofile(state->lua_state, "./lua/export.lua")) {
    printf("lua loadtime error: %s\n", lua_tostring(state->lua_state, -1));
  }

  lua_getglobal(state->lua_state, "compile");

  if (lua_pcall(state->lua_state, 0, 1, 0) != 0) {
    printf("lua runtime error: %s\n", lua_tostring(state->lua_state, -1));
  }

  return state;
}

void tulip_compiler_stop(tulip_compiler_state* state) {
  lua_close(state->lua_state);
}
