CC=gcc
CFLAGS=-std=c11 -Wall -Wextra -Werror -Wpedantic -pedantic-errors

tag: tag.o
	$(CC) -o tag $<

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $<

clean:
	rm -rf tag tag.o
