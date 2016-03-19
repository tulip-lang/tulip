#pragma once

#include "types/value.h"

typedef struct tulip_tag {
  char* tag_name;
  unsigned int length;
  tulip_value_t* contents;
} tulip_tag_t;


tulip_tag_t* build_tag(char* name, unsigned int length, tulip_value_t* contents);
tulip_tag_t* append_tag(tulip_tag_t* t, tulip_value_t v);
char* show_tag(tulip_tag_t* t);
