from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner
from cocotb.clock import Clock

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


@cocotb.test()
async def fifo_basic_test(dut):
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())

    #reset the dut
    dut.rst.value = 1
    #initialize all other inputs
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value   = 0

    for _ in range(2):
        await RisingEdge(dut.clk)
     
    dut.rst.value = 0
    await RisingEdge(dut.clk)   # one clean cycle before driving

    # Write then read using coroutines
    await fifo_write(dut, 0xAB)
    result = await fifo_read(dut)

    dut._log.info(f"dout = {result:#04x}")
    

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