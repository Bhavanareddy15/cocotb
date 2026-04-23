TOPLEVEL_LANG ?= verilog

PWD=$(shell pwd)

# design/ is one level up from tb/
DESIGN_DIR = $(PWD)/../design

# Add tb/ to PYTHONPATH so AXI4_utils.py is importable
export PYTHONPATH := $(PWD):$(PYTHONPATH)

ifeq ($(TOPLEVEL_LANG),verilog)
    VERILOG_SOURCES = $(DESIGN_DIR)/axi4_lite_master.sv \
                      $(DESIGN_DIR)/axi4_lite_slave.sv  \
                      $(DESIGN_DIR)/axi4_lite_top.sv
else
    $(error A valid value (verilog or vhdl) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG))
endif

COCOTB_TOPLEVEL     := axi4_lite_top
COCOTB_TEST_MODULES := AXI4_tb_top     # maps to tb/axi4_tb_pyuvm.py

# Default test — can override on command line: make TEST=RandomWriteReadTest
COCOTB_TESTCASE ?= WriteReadBackTest

include $(shell cocotb-config --makefiles)/Makefile.sim
