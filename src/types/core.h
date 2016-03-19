// canonical representation of tulip ast as a tag tree

#include <stdbool.h>

#include "types/value.h"

tulip_value_t* cons(tulip_value_t* array, int length);
bool validate_cons(tulip_value_t* subject);
tulip_value_t* block(tulip_value_t* contents, int length);
bool validate_block(tulip_value_t* subject);
tulip_value_t* branch(tulip_value_t* predicates, tulip_value_t* conseuqnces, int length);
