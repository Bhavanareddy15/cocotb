import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb.clock    import Clock
import pyuvm
from pyuvm import uvm_test

from async_fifo_sequences import FifoReadSeq, FifoWriteSeq
 
import sys, os
 
from async_fifo_env import FifoEnv
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
 
async def start_clocks(dut):
    cocotb.start_soon(Clock(dut.wclk, 8,  unit="ns").start())
    cocotb.start_soon(Clock(dut.rclk, 20, unit="ns").start())
 
 
async def apply_reset(dut, cycles=5):
    dut.w_rst_n.value = 0
    dut.r_rst_n.value = 0
    dut.w_en.value    = 0
    dut.r_en.value    = 0
    dut.data_in.value = 0
    await ClockCycles(dut.wclk, cycles)
    dut.w_rst_n.value = 1
    dut.r_rst_n.value = 1
    await ClockCycles(dut.wclk, 2)
 

 
 
# ─────────────────────────────────────────────────────────────────────────────
# Base test
# ─────────────────────────────────────────────────────────────────────────────
 
class AsyncFifoBase(uvm_test):
    def build_phase(self):
        self.env = FifoEnv("env", self)
 
    async def run_phase(self):
        self.raise_objection()
        dut = cocotb.top
        await start_clocks(dut)
        await apply_reset(dut)
        await self.do_test(dut)
        await ClockCycles(dut.wclk, 30)
        self.drop_objection()
 
    async def do_test(self, dut):
        cocotb.start_soon(FifoReadSeq.start(self.env.write_agent.seqr))
        await FifoReadSeq.start(self.env.read_agent.seqr)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Reset
# ─────────────────────────────────────────────────────────────────────────────
 
@pyuvm.test()
class TestReset(AsyncFifoBase):
    async def do_test(self, dut):
        await Timer(1, "step")
        assert int(dut.empty.value) == 1, "empty must be 1 after reset"
        assert int(dut.full.value)  == 0, "full must be 0 after reset"
        self.logger.info("Initial flags OK: empty=1, full=0")

        # write some data using the sequencer
        write_seq       = FifoWriteSeq("write_seq")
        write_seq.count = 5
        await write_seq.start(self.env.write_agent.seqr)
        await ClockCycles(dut.wclk, 4)

        # mid-sim reset
        dut.w_rst_n.value = 0
        dut.r_rst_n.value = 0
        await ClockCycles(dut.wclk, 4)
        await Timer(1, "step")
        assert int(dut.empty.value) == 1, "empty must be 1 after mid-sim reset"
        assert int(dut.full.value)  == 0, "full must be 0 after mid-sim reset"
        dut.w_rst_n.value = 1
        dut.r_rst_n.value = 1
        self.logger.info("Mid-sim re-reset: empty=1, full=0 ✓")