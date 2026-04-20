TOPLEVEL_LANG ?= verilog
 
PWD=$(shell pwd)
 
# tb/ is where this Makefile lives; design/ is one level up
DESIGN_DIR = $(PWD)/../design
 
# Add tb/ to PYTHONPATH so axi4_bfm.py is importable from axi4_tb_top.py
export PYTHONPATH := $(PWD):$(PYTHONPATH)
 
ifeq ($(TOPLEVEL_LANG),verilog)
    VERILOG_SOURCES = $(DESIGN_DIR)/axi4_lite_master.sv \
                      $(DESIGN_DIR)/axi4_lite_slave.sv  \
                      $(DESIGN_DIR)/axi4_lite_top.sv
else
    $(error A valid value (verilog or vhdl) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG))
endif
 
COCOTB_TOPLEVEL     := axi4_lite_top
COCOTB_TEST_MODULES := axi4_tb_top   # maps to tb/axi4_tb_top.py
 
include $(shell cocotb-config --makefiles)/Makefile.sim