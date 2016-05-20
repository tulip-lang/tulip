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
<<<<<<< HEAD
	clang $(cflags) $(srcs) -o build/rt
=======
	mkdir -p build
	clang $(cflags) src/types/core.c src/types/value.c src/types/scaffold.c -o build/core
>>>>>>> 90ff531ea927db86ed90b3c1be5ddf60268ea583
