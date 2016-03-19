cflags = --std=c11 -Isrc/ -g

.PHONY: build run clean

build: types
run:
	./build/tag
clean:
	rm build/**

types:
	clang $(cflags) src/types/core.c src/types/value.c src/types/scaffold.c -o build/tag
