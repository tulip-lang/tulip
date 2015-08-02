# -*- configurable options -*- #
EXTERNALS ?= ./.externals
PYTHON ?= python2

BUILD_OPTS ?= --thread --no-shared --gcrootfinder=shadowstack
JIT_OPTS ?= --opt=jit

TARGET ?= target.py

# -*- constants -*- #
PYPY_DIR=$(EXTERNALS)/pypy
PYPY_TARGET=$(PYPY_DIR)/.make-target
PYTHONPATH = $$PYTHONPATH:$(PYPY_DIR)
RPYTHON_EXEC = $(PYTHON) $(PYPY_DIR)/rpython/bin/rpython $(BUILD_OPTS)
PYTHON_EXEC = PYTHONPATH=$(PYTHONPATH) $(PYTHON)

# -*- default help action -*- #
.PHONY: help
help:
	@echo "make help                   - display this message"
	@echo "make build                  - build the interpreter"
	@echo "make fetch-externals        - download and unpack external deps"
	@echo "make run                    - run the Tulip repl"
	@echo "make clean                  - remove build files"
	@echo "make pyrepl                 - run a python repl with the correct paths set"

# -*- externals -*- #
.PHONY: fetch-externals
fetch-externals: $(PYPY_TARGET)

.PHONY: pyrepl
pyrepl:
	$(PYTHON_EXEC)

$(PYPY_TARGET):
	mkdir -p $(dir $@)
	curl https://bitbucket.org/pypy/pypy/get/default.tar.bz2 \
	  | tar -xjf - -C $(EXTERNALS)/pypy --strip-components=1
	touch $@

# -*- build -*- #
DIST_BIN = ./dist/bin/tulip
CLEAN += $(DIST_BIN)
SOURCE = $(TARGET) $(shell find tulip -name '*.py')

$(DIST_BIN): $(PYPY_TARGET) $(SOURCE)
	mkdir -p $(dir $@)
	$(RPYTHON_EXEC) $(TARGET) && mv target-c $@

.PHONY: build
build: $(DIST_BIN)

.PHONY: run
run: $(DIST_BIN)
	$(DIST_BIN)

.PHONY: run-interpreted
run-interpreted: $(PYPY_TARGET)
	$(PYTHON_EXEC) $(TARGET) $(ARGS)


.PHONY: clean
clean:
	rm -rf $(CLEAN)
