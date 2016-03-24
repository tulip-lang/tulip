// unified representation for tulip values

#pragma once

typedef struct tulip_literal {
  enum literal_tag { TULIP_LITERAL_STRING
                   , TULIP_LITERAL_NUMBER
                   } type;
  union {
    char* string;
    double number;
  };
} tulip_literal;

// forward decl
typedef struct tulip_value tulip_value;

typedef struct tulip_tag {
  char* name;
  unsigned int length;
  tulip_value* contents;
} tulip_tag;

typedef struct tulip_value {
  enum value_tag { TULIP_VALUE_LITERAL
                 , TULIP_VALUE_CLOSURE
                 , TULIP_VALUE_TAG
                 } type;
  union {
    tulip_literal literal;
    void* closure;
    tulip_tag tag;
  };
} tulip_value;

tulip_value build_string(char* s);
tulip_value build_number(double n);
tulip_value build_tag(char* name, unsigned int length, tulip_value contents[]);
char*       show_value(tulip_value v);

tulip_tag*  append_tag(tulip_tag* t, tulip_value v);
