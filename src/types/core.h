// canonical representation of tulip ast as a tag tree

#include <stdbool.h>

#include "types/value.h"

#pragma once

tulip_value cons(tulip_value* array, int length);
bool validate_cons(tulip_value subject);
tulip_value block(tulip_value* contents, int length);
bool validate_block(tulip_value subject);
tulip_value branch(tulip_value* predicates, tulip_value* conseuqnces, int length);
