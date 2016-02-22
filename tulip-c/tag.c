#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef union tulip_value {
  char*  literal_string;
  double  literal_number;
  void* closure;
  struct tulip_tag* tag;
} tulip_value_t;

typedef struct tulip_tag {
  char* tag_name;
  unsigned int length;
  tulip_value_t* contents;
} tulip_tag_t;

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

char* show_value(tulip_value_t* v) {
  char* s = (char*) v;
  return s;
}

char* show_tag(tulip_tag_t* t) {
  (void) t;
  return NULL;
}


int main() {
  tulip_value_t* v1 = malloc(2*sizeof(tulip_value_t));
  tulip_value_t* v2 = malloc(2*sizeof(tulip_value_t));
  memcpy(v1,
    (tulip_value_t []){
        (tulip_value_t) {.literal_string = "tree"}, \
        (tulip_value_t) {.literal_string = "nesting"} \
    }, \
    2*sizeof(tulip_value_t));
  
  tulip_tag_t* inner = build_tag("branch", 2, v1);
  memcpy(v2,
    (tulip_value_t []){
      (tulip_value_t) {.literal_string = "test"}, \
      (tulip_value_t) {.tag = inner} \
    }, \
    2*sizeof(tulip_value_t));
  tulip_tag_t* outer = build_tag("branch", 2, v2);

  printf("%s", outer->contents[1].tag->contents[1].literal_string);

  return 0;
}
