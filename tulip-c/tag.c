#include <stdlib.h>
#include <stdio.h>

struct tulip_tag;

typedef union tulip_value {
  char*  literal_string;
  double  literal_number;
  size_t* closure;
  struct tulip_tag* tag;
} tulip_value;

typedef struct tulip_tag {
  char* tag_name;
  int length;
  tulip_value* contents;
} tulip_tag;

tulip_tag* build_tag(char* name, tulip_value* contents) {
  int l = sizeof(contents) / sizeof(tulip_value);

  if (l < 5) {
    tulip_value* p = realloc(contents, sizeof(tulip_value[5]));

    if (p) {
      return &(tulip_tag){name, l, p};
    } else {
      printf("array resize failed");
      return NULL;
    }
  } else {
    return &(tulip_tag){name, l, contents};
  }
}

tulip_tag* append_tag(tulip_tag* t, tulip_value v) {
  if(t->length >= 5) {
    tulip_value* p = realloc(t->contents, sizeof(tulip_value[t->length + 1]));
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

char* show_value(tulip_value* v) {
  char* s = (char*) v;
  return s;
}

char* show_tag(tulip_tag* t) {
};


int main() {
  tulip_value v1[] = {(tulip_value) "tree", (tulip_value) "nesting"};
  tulip_tag* inner = build_tag("branch", v1);
  tulip_value v2[] = {(tulip_value) "test", (tulip_value) inner};
  tulip_tag* outer = build_tag("branch", v2);

  printf("%s", (char*) &outer->contents[0]);

  return 0;
}
