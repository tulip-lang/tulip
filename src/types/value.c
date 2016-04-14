// constructors and invariant checks for tulip-core's base value types
// documented more rigorously in doc/core.org

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "types/value.h"

char* show_value(tulip_value v) {
  if (v.type == TULIP_VALUE_LITERAL) {
    if (v.literal.type == TULIP_LITERAL_STRING) {
      char* str = malloc(sizeof(char) * (strlen(v.literal.string) + 2));
      sprintf(str, "\"%s\"", v.literal.string);
      return str;
    } else if(v.literal.type == TULIP_LITERAL_NUMBER) {
      char* str = malloc(sizeof(char) * 10);     // length is arbitrary
      snprintf(str, 10, "%g", v.literal.number); // because this doesn't pad right
      return str;
    }
    return "invalid literal";
  } else if (v.type == TULIP_VALUE_TAG) {
    if (0 < v.tag.length) {
      // todo implement tree printing
      char* str = malloc(sizeof(char) * strlen(v.tag.name) + 5);
      sprintf(str, ".%s ...", v.tag.name);
      return str;
    } else {
      char* str = malloc(sizeof(char) * strlen(v.tag.name) + 1);
      sprintf(str, ".%s", v.tag.name);
      return str;
    }
  } else {
    return "you can't print this silly";
  }
}

tulip_value build_string(char* s) {
  return (tulip_value) { .type = TULIP_VALUE_LITERAL
                       , .literal = (tulip_literal) { .type = TULIP_LITERAL_STRING
                                                    , .string = s
                                                    }
                       };
}

tulip_value build_number(double n) {
  return (tulip_value) { .type = TULIP_VALUE_LITERAL
                       , .literal = (tulip_literal) { .type = TULIP_LITERAL_NUMBER
                                                    , .number = n
                                                    }
                       };
}

tulip_value build_tag(char* name, unsigned int length, tulip_value contents[]) {
  tulip_value* c = (length < 5) ? malloc(sizeof(tulip_value) * 5)
                                : malloc(sizeof(tulip_value) * length);

  if (contents != NULL) memcpy(c, contents, sizeof(tulip_value) * length);

  return (tulip_value) { .type = TULIP_VALUE_TAG
                       , .tag = (tulip_tag) { .name = name
                                            , .length = length
                                            , .contents = c
                                            }
                       };
}

tulip_tag* append_tag(tulip_tag* t, tulip_value v) {
  if(t->length >= 5) {
    tulip_value* p = realloc(t->contents, sizeof(tulip_value[t->length + 1]));
    if(p) {
      t->contents[t->length] = v;
      t->length += 1;
    } else {
      // todo better error handling
      printf("array resize failed");
    }
  } else {
    t->contents[t->length] = v;
    t->length += 1;
  }

  return t;
}

bool validate_tag(tulip_value t) {
  // failed malloc or constructor not used
  if (t.tag.contents == NULL)
    return false;

  // pointer paranoia, the utility of this check is questionable
  if (t.tag.contents == &t || t.tag.contents == &t.tag)
    return false;

  // name is either empty or \0
  if (t.tag.name == NULL)
    return false;

  return true;
}
