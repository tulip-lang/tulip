cflags = --std=c11 -Isrc/ -g -lm -lLLVM -l"lua5.2"
srcs   = src/types/core.c src/types/value.c src/runtime/init.c src/compiler/host.c src/main.c

.PHONY: build run clean help

build: binary
run:
	./build/tulip
clean:
	rm build/**
help:
  echo "targets: build, run, clean"

binary:
	mkdir -p build
	clang $(cflags) $(srcs) -o build/tulip

# library:
