TOPLEVEL_LANG ?= verilog
 
 
PWD=$(shell pwd)
export PYTHONPATH := $(PWD):$(PYTHONPATH)
 
ifeq ($(TOPLEVEL_LANG),verilog)
    VERILOG_SOURCES = $(PWD)/design.sv
else
    $(error A valid value (verilog or vhdl) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG))
endif
 
COCOTB_TOPLEVEL     := fifo_sync
COCOTB_TEST_MODULES := test_FIFO
 
include $(shell cocotb-config --makefiles)/Makefile.sim