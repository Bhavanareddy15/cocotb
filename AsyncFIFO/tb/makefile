# ─────────────────────────────────────────────────────────────────────────────
# Async FIFO  —  cocotb + pyuvm Makefile
# Simulator: icarus (default) | questa | vcs
#
# Usage:
#   make                     run all tests with Icarus
#   make SIM=questa          run with Questa
#   make TEST=TestReset      run a single named test
#   make WAVES=1             open GTKWave after run (Icarus only)
# ─────────────────────────────────────────────────────────────────────────────

SIM           ?= icarus
TOPLEVEL       = top
TOPLEVEL_LANG  = verilog

# Design sources — include order matters for `include chains
VERILOG_SOURCES += $(realpath ../design/intfc.sv)
VERILOG_SOURCES += $(realpath ../design/w2rsync.sv)
VERILOG_SOURCES += $(realpath ../design/r2wsync.sv)
VERILOG_SOURCES += $(realpath ../design/write_ptr.sv)
VERILOG_SOURCES += $(realpath ../design/read_ptr.sv)
VERILOG_SOURCES += $(realpath ../design/fifo_mem.sv)
VERILOG_SOURCES += $(realpath ../design/top.sv)

# Simulator-specific flags
ifeq ($(SIM),icarus)
  COMPILE_ARGS += -g2012
endif
ifeq ($(SIM),questa)
  COMPILE_ARGS += -sv
  SIM_ARGS     += -do "log -r /*; run -all"
endif
ifeq ($(SIM),vcs)
  COMPILE_ARGS += -sverilog +v2k
endif

ifeq ($(SIM),verilator)
  COMPILE_ARGS += --timing        # required for cocotb with Verilator
  COMPILE_ARGS += --assert        # enable SVA (partial support)
  COMPILE_ARGS += -Wall           # recommended
  COMPILE_ARGS += -I$(DESIGN_DIR)
endif
# Python test module (relative to PYTHONPATH root)
COCOTB_TEST_MODULES = test_async_fifo

# Single-test shortcut
ifdef TEST
  TESTCASE = $(TEST)
endif

# PYTHONPATH must point to project root so "from tb.xxx" resolves
export PYTHONPATH := $(realpath ..):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: waves clean_all
waves:
	gtkwave dump.vcd &

clean_all: clean
	rm -rf __pycache__ results.xml dump.vcd sim_build