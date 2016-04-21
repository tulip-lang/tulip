#pragma once

#include <stdlib.h>
#include <stdbool.h>

// todo move these macro definitions somewhere more sensible
#define __STDC_LIMIT_MACROS
#define __STDC_CONSTANT_MACROS

#include <llvm-c/Core.h>
#include <llvm-c/ExecutionEngine.h>

typedef struct tulip_runtime_allocator {
  void* region;
  size_t width;
  int length;
} tulip_runtime_allocator;

typedef struct tulip_runtime_state {
  tulip_runtime_allocator allocator;
  LLVMModuleRef toplevel_module;
  LLVMExecutionEngineRef jit_instance;

} tulip_runtime_state;

bool tulip_allocator_new(int length);
bool tulip_allocator_alloc();
bool tulip_allocator_free();

tulip_runtime_state tulip_runtime_start();
void tulip_runtime_stop(tulip_runtime_state rt);
