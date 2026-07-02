import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb.clock    import Clock
import pyuvm
from pyuvm import uvm_test

from async_fifo_sequences import FifoReadSeq, FifoWriteSeq, FifoFillSeq
 
import sys, os
 
from async_fifo_env import FifoEnv

FIFO_DEPTH = 256
 
 
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
        pass
 
 
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

# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Write and then Read
# ─────────────────────────────────────────────────────────────────────────────

@pyuvm.test()
class TestWriteRead(AsyncFifoBase):
    async def do_test(self, dut):
        write_seq       = FifoWriteSeq("write_seq")
        write_seq.count = 8
        await write_seq.start(self.env.write_agent.seqr)

        await ClockCycles(dut.wclk, 10)

        read_seq       = FifoReadSeq("read_seq")
        read_seq.count = 8
        await read_seq.start(self.env.read_agent.seqr)

        await ClockCycles(dut.rclk, 10)
        self.logger.info("TestWriteRead complete")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Full Flag
# ─────────────────────────────────────────────────────────────────────────────



async def count_accepted_writes(dut, counter):
    """Independently tracks how many writes the DUT actually accepts,
    instead of trusting the driver's dispatched-item count. A write is
    accepted iff w_en=1 and full=0 at the sampled wclk edge — matching
    the RTL's own waddr_next = waddr + (w_en & !full) logic."""
    while True:
        await RisingEdge(dut.wclk)
        if int(dut.w_en.value) == 1 and int(dut.full.value) == 0:
            counter[0] += 1


@pyuvm.test()
class TestFullFlag(AsyncFifoBase):
    async def do_test(self, dut):
        accepted = [0]
        cocotb.start_soon(count_accepted_writes(dut, accepted))

        # ── Fill the FIFO ──────────────────────────────────────────
        # Dispatch more items than the FIFO can hold, so we can also
        # verify overflow attempts are correctly rejected.
        write_seq       = FifoFillSeq("write_seq")
        write_seq.count = FIFO_DEPTH + 20
        assert int(dut.full.value) == 0, "full is zero before start of the test"
        await write_seq.start(self.env.write_agent.seqr)

        await ClockCycles(dut.rclk, 4)
        await ClockCycles(dut.wclk, 4)

        assert int(dut.full.value) == 1, "full must assert once FIFO is full"
        assert accepted[0] == FIFO_DEPTH, (
            f"expected exactly {FIFO_DEPTH} writes accepted, "
            f"but DUT actually accepted {accepted[0]} "
            f"(dispatched {write_seq.count} items to the driver)"
        )
        self.logger.info(
            f"full=1 after {accepted[0]} real accepted writes "
            f"(driver dispatched {write_seq.count}, "
            f"{write_seq.count - accepted[0]} correctly suppressed) ✓"
        )

        # ── Confirm no further writes are silently accepted ────────
        held_count = accepted[0]

        overflow_seq       = FifoFillSeq("overflow_seq")
        overflow_seq.count = 5
        await overflow_seq.start(self.env.write_agent.seqr)

        await ClockCycles(dut.wclk, 4)
        assert int(dut.full.value) == 1, "full must stay asserted after overflow attempts"
        assert accepted[0] == held_count, "no additional writes should be accepted while full"
        self.logger.info("Overflow correctly suppressed ✓")

        # ── Now read one entry — full must deassert ────────────────
        read_seq       = FifoReadSeq("read_seq")
        read_seq.count = 1
        await read_seq.start(self.env.read_agent.seqr)

        await ClockCycles(dut.rclk, 4)
        await ClockCycles(dut.wclk, 4)
        assert int(dut.full.value) == 0, "full must deassert after one read"
        self.logger.info("full deasserted after one read ✓")

        self.logger.info("TestFullFlag complete")