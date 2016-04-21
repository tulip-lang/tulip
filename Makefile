cflags = --std=c11 -Isrc/ -g -lm -lLLVM
srcs   = src/types/core.c src/types/value.c src/runtime/init.c src/main.c

.PHONY: build run clean

build: types
run:
	./build/rt
clean:
	rm build/**

# TODO smarter makefile
types:
	clang $(cflags) $(srcs) -o build/rt
