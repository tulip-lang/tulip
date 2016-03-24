#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "types/value.h"
#include "types/core.h"

int main() {

  tulip_value vs[] = {build_string("test-string-1"), build_number(12.34)};
  tulip_value null_tag = build_tag("nil", 0, NULL);

  printf("string printing: %s\n", show_value(vs[0]));
  printf("number printing: %s\n", show_value(vs[1]));

  printf("niladic tag printing: %s\n", show_value(null_tag));

  tulip_value pair[] = {build_string("one"), build_string("two")};
  tulip_value list = cons(pair, 2);

  printf("cons head value: %s\n", show_value(list.tag.contents[0]));
  printf("cons tail head value: %s\n", show_value(list.tag.contents[1].tag.contents[0]));

  tulip_value triplet[] = {build_string("one"), build_string("two"), build_string("three")};
  tulip_value long_cons = cons(triplet, 3);

  printf("cons head vals: [%s, %s, %s]\n", show_value(long_cons.tag.contents[0]), show_value(long_cons.tag.contents[1].tag.contents[0]), show_value(long_cons.tag.contents[1].tag.contents[1].tag.contents[0]));

  tulip_value block_test = block(triplet, 3);
  printf("block node: %s", show_value(block_test));

  return 0;
}
