.PHONY: all run run-gaussian clean

LAZER_DIR  = ../../lazer
SCRIPTS    = $(LAZER_DIR)/scripts
PYTHON_DIR = $(LAZER_DIR)/python

all: _client_nizk_params_cffi.o _server_nizk_params_cffi.o _server_nizk_gaussian_params_cffi.o

_client_nizk_params_cffi.o: client_nizk_params.h $(PYTHON_DIR)/_lazer_cffi.o
	python3 $(PYTHON_DIR)/params_cffi_build.py client_nizk_params.h $(LAZER_DIR)

_server_nizk_params_cffi.o: server_nizk_params.h $(PYTHON_DIR)/_lazer_cffi.o
	python3 $(PYTHON_DIR)/params_cffi_build.py server_nizk_params.h $(LAZER_DIR)

_server_nizk_gaussian_params_cffi.o: server_nizk_gaussian_params.h $(PYTHON_DIR)/_lazer_cffi.o
	python3 $(PYTHON_DIR)/params_cffi_build.py server_nizk_gaussian_params.h $(LAZER_DIR)

client_nizk_params.h: client_nizk_params.py
	cd $(SCRIPTS) && sage lin-codegen.sage $(CURDIR)/client_nizk_params.py > $(CURDIR)/client_nizk_params.h

server_nizk_params.h: server_nizk_params.py
	cd $(SCRIPTS) && sage lin-codegen.sage $(CURDIR)/server_nizk_params.py > $(CURDIR)/server_nizk_params.h

server_nizk_gaussian_params.h: server_nizk_gaussian_params.py
	cd $(SCRIPTS) && sage lin-codegen.sage $(CURDIR)/server_nizk_gaussian_params.py > $(CURDIR)/server_nizk_gaussian_params.h

$(PYTHON_DIR)/_lazer_cffi.o:
	cd $(PYTHON_DIR) && make

run: all
	python3 nizks.py

run-gaussian: all
	python3 nizks_gaussian.py

clean:
	rm -rf __pycache__
	rm -f *.c *.o *.so
