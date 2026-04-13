from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner
from cocotb.clock import Clock

from fifo_model import FifoModel

async def fifo_write(dut, data):
    dut.wr_en.value = 1
    dut.din.value   = data
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0

async def fifo_read(dut):
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)   # dout is registered, wait one extra cycle
    return int(dut.dout.value)

async def reset(dut):
    dut.rst.value   = 1
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value   = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def fifo_full_test(dut):
    """Write until full, verify full flag, ensure no overflow corruption."""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)
    await reset(dut)

    for i in range(4):  # fill all 4 slots
        await fifo_write(dut, i)
        model.write(i)

    await RisingEdge(dut.clk)  

    assert dut.full.value  == 1       #should be full
    assert dut.empty.value == 0        #should not be empty
    assert dut.full.value  == model.full() #full flag mismatch

    # Extra write while full — should be silently dropped
    await fifo_write(dut, 0xFF)
    assert dut.full.value == 1 #"still full after overflow attempt"

@cocotb.test()
async def fifo_empty_test(dut):
    """Fill then drain completely, verify empty flag."""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)
    await reset(dut)

    for i in range(4):
        await fifo_write(dut, i)
        model.write(i)

    for _ in range(4):
        result      = await fifo_read(dut)
        model_result = model.read()
        assert result == model_result, f"DUT={result:#04x} model={model_result:#04x}"

    assert dut.empty.value == 1 , "should be empty after draining"

    # Extra read while empty — dout should not change / no crash
    stale_dout = int(dut.dout.value)
    await fifo_read(dut)
    assert int(dut.dout.value) == stale_dout, "dout changed on underflow read"

@cocotb.test()
async def fifo_concurrent_test(dut):
    """Assert rd_en and wr_en in the same cycle — count must stay stable."""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)
    await reset(dut)

    # Pre-load one item
    await fifo_write(dut, 0xAA)
    model.write(0xAA)

    await RisingEdge(dut.clk)
    # Simultaneous read+write
    dut.wr_en.value = 1
    dut.rd_en.value = 1
    dut.din.value   = 0xBB
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    model.write(0xBB)
    model.read()     # net zero — count unchanged

    await RisingEdge(dut.clk)

    # One item (0xBB) should remain
    result = await fifo_read(dut)
    expected_res=model.read()
    assert result == expected_res, f"{expected_res: #04x} after concurrent rw, got {result:#04x}"
    assert dut.empty.value == model.empty(), "empty flag mismatch after concurrent rw"
@cocotb.test()
async def fifo_random_test(dut):
    """Random interleaved writes and reads against the software model."""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)
    await reset(dut)

    for _ in range(200):
        action = random.choice(["write", "read", "idle"])

        if action == "write" and not model.full():
            data = random.randint(0, 0xFF)
            await fifo_write(dut, data)
            model.write(data)
            await RisingEdge(dut.clk)

        elif action == "read" and not model.empty():
            result       = await fifo_read(dut)
            model_result = model.read()
            assert result == model_result, (
                f"Random test mismatch: DUT={result:#04x} model={model_result:#04x}"
            )

        else:
            await RisingEdge(dut.clk)

        assert dut.full.value  == model.full(),  "full flag mismatch"
        assert dut.empty.value == model.empty(), "empty flag mismatch"


@cocotb.test()
async def fifo_basic_test(dut):
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)

    await reset(dut)

    # Write then read using coroutines
    await fifo_write(dut, 0xAB)
    model.write(0xAB)
    result = await fifo_read(dut)
    model_result = model.read()

    dut._log.info(f"dout = {result:#04x}")

    assert result == model_result, (
        f"Mismatch: DUT={result:#04x}, model={model_result:#04x}"
    )

    # Flag checks
    assert dut.full.value  == model.full(),  "full flag mismatch"
    assert dut.empty.value == model.empty(), "empty flag mismatch"


@cocotb.test()
async def fifo_reset_midop_test(dut):
    """Assert reset while FIFO has data — all state must clear."""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    model = FifoModel(depth=4)
    await reset(dut)

    for d in [0x11, 0x22, 0x33]:
        await fifo_write(dut, d)
        await RisingEdge(dut.clk)
        model.write(d)

    # Mid-operation reset
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    model = FifoModel(depth=4)  # reset software model too
    await RisingEdge(dut.clk)

    assert dut.empty.value == 1, "not empty after mid-op reset"
    assert dut.full.value  == 0, "full asserted after reset"
    assert int(dut.dout.value) == 0, "dout not cleared after reset"   

def test_fifo_runner():
    """Simulate fifo_debug using the Python runner.
 
    This file can be run directly or via pytest discovery.
    """
    sim = os.getenv("SIM", "icarus")
 
    proj_path = Path(__file__).resolve().parent
 
    sources = [proj_path / "design.sv"]
 
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fifo_sync",
        always=True,
        build_args=["-g2012", "-DTIMESCALE"],  # set timescale
        timescale=("1ns", "1ps"),              # time unit, time precisio
    )
    runner.test(
        hdl_toplevel="fifo_sync",
        test_module="test_FIFO",
        
    )
 
 
if __name__ == "__main__":
    test_fifo_runner()