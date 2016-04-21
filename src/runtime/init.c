#include "runtime/init.h"

#include <stdio.h>

#define __STDC_LIMIT_MACROS
#define __STDC_CONSTANT_MACROS

#include <llvm-c/Initialization.h>
#include <llvm-c/Core.h>
#include <llvm-c/Target.h>
#include <llvm-c/ExecutionEngine.h>

// i'm going to document this really verbosely until it gets broken apart
tulip_runtime_state tulip_runtime_start() {
  tulip_runtime_state state;

  printf("initializing llvm\n");

  // llvm allocates a static pass registry on load, this retrieves it
  // i think the c++ api must perform this implicitly, it was fairly hard to figure out for something so simple & crucial
  LLVMPassRegistryRef pass = LLVMGetGlobalPassRegistry();

  // initializing core just performs some allocations for non-critical stuff like printing the ir in text format
  LLVMInitializeCore(pass);

  // llvm supposedly implicitly initializes the local machine target on load, but on a lot of systems (?-apple-darwin especially) i've found that is unreliable and it's better to just init them explicitly
  // i load all of them because it's cheap
  LLVMInitializeAllTargetInfos();
  LLVMInitializeAllTargets();
  LLVMInitializeAllTargetMCs();


  printf("llvm initialized\n");

  printf("initializing toplevel module\n");

  // the module target may be set implicitly, i haven't tested this as much
  state.toplevel_module = LLVMModuleCreateWithName("tulip-toplevel");
  LLVMSetTarget(state.toplevel_module, "x86_64-unknown-linux-gnu");

  printf("toplevel initialized\n");

  printf("initializing mcjit\n");

  // mcjit symbols are not linked by default
  LLVMLinkInMCJIT();
  struct LLVMMCJITCompilerOptions o;
  LLVMInitializeMCJITCompilerOptions(&o, sizeof(o));
  // jit option flags can be set here
  char** error;

  // it's likely that we'll want multiple modules (one for each process) with a shared mcjit instance, but for now it's safe to run it like this
  if(LLVMCreateMCJITCompilerForModule(&(state.jit_instance), state.toplevel_module, &o, sizeof(o), error)) {
    printf("initialized mcjit\n");
  } else {
    printf("%s\n", error);
  }

  return state;
}

void tulip_runtime_stop(tulip_runtime_state rt) {
  LLVMDisposeModule(rt.toplevel_module);
  LLVMDisposeExecutionEngine(rt.jit_instance);
  LLVMShutdown();
}
