#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "types/tag.h"

tulip_tag_t* build_tag(char* name, unsigned int length, tulip_value_t* contents) {
    tulip_tag_t * t = malloc(sizeof(tulip_tag_t));

    if(t == NULL) {
      printf("Tag allocation failed");
      return NULL;
    }

    if (length < 5) {
      tulip_value_t* p = realloc(contents, 5*sizeof(tulip_value_t));

      if (p) {
        *t = (tulip_tag_t){name, length, p};
      } else {
        printf("array resize failed");
        return NULL;
      }
    } else {
      *t = (tulip_tag_t){name, length, contents};
    }

    return t;
}

tulip_tag_t* append_tag(tulip_tag_t* t, tulip_value_t v) {
  if(t->length >= 5) {
    tulip_value_t* p = realloc(t->contents, sizeof(tulip_value_t[t->length + 1]));
    if(p) {
      t->contents[t->length] = v;
      t->length += 1;
    } else {
      printf("array resize failed");
    }
  } else {
    t->contents[t->length] = v;
    t->length += 1;
  }

  return t;
}

char* show_tag(tulip_tag_t* t) {
  (void) t;
  return NULL;
}

