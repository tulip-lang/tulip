// unified representation for tulip values

#pragma once

typedef union tulip_value {
  char*  literal_string;
  double  literal_number;
  void* closure;
  struct tulip_tag* tag;
} tulip_value_t;

char* show_value(tulip_value_t* v);

// TEMPORARY TAG IMPORT

typedef struct tulip_tag {
  char* tag_name;
  unsigned int length;
  tulip_value_t* contents;
} tulip_tag_t;


tulip_tag_t* build_tag(char* name, unsigned int length, tulip_value_t* contents);
tulip_tag_t* append_tag(tulip_tag_t* t, tulip_value_t v);
char* show_tag(tulip_tag_t* t);
