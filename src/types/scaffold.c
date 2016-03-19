#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "types/value.h"
#include "types/core.h"

int main_() {
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

int main() {
  int list_length = 2;

  tulip_value_t list[] = { (tulip_value_t) {.literal_string = "head"}
                         , (tulip_value_t) {.literal_string = "tail"}
                         };

  tulip_value_t* list_cons = cons(list, list_length);

  printf("reading value\n");
  printf("%s", (*list_cons).tag->contents[0].);

  return 0;
}
