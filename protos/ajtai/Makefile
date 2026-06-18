.PHONY: all run clean

LAZER_DIR  = ../../lazer
SCRIPTS    = $(LAZER_DIR)/scripts
PYTHON_DIR = $(LAZER_DIR)/python

all: _params_cffi.o

_params_cffi.o: params.h $(PYTHON_DIR)/_lazer_cffi.o
	python3 $(PYTHON_DIR)/params_cffi_build.py params.h $(LAZER_DIR)

params.h: params.py
	cd $(SCRIPTS) && sage lin-codegen.sage $(CURDIR)/params.py > $(CURDIR)/params.h

$(PYTHON_DIR)/_lazer_cffi.o:
	cd $(PYTHON_DIR) && make

run: all
	python3 demo.py

clean:
	rm -rf __pycache__
	rm -f *.c *.o *.so
