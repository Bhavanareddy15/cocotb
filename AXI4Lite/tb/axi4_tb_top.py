import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_tools.runner import get_runner
from cocotb.clock import Clock

from axi4_bfm import reset_dut, axi_write, axi_read, CLK_PERIOD

@cocotb.test()
async def tc01_reset_correctness(dut):
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit= "ns").start())
    dut.ARESETN.value = 0
    dut.read_s.value  = 0
    dut.write_s.value = 0
    await RisingEdge(dut.ACLK)
    await RisingEdge(dut.ACLK)
    assert int(dut.u_axi4_lite_master0.state.value) == 0, "Master not reset correctly"

    assert int(dut.u_axi4_lite_slave0.state.value) == 0, "Slave not reset correctly"

    # Also verify all output signals are deasserted
    assert dut.u_axi4_lite_master0.M_ARVALID.value == 0, "M_ARVALID not deasserted"
    assert dut.u_axi4_lite_master0.M_AWVALID.value == 0, "M_AWVALID not deasserted"
    assert dut.u_axi4_lite_master0.M_WVALID.value  == 0, "M_WVALID not deasserted"

    # Verify all 32 slave registers are zero
    for i in range(32):
        val = int(dut.u_axi4_lite_slave0.register[i].value)
        assert val == 0, f"register[{i}] = 0x{val:08X}, expected 0x00000000"

@cocotb.test()
async def tc02_idle_stability(dut):
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut,2)
    await ClockCycles(dut.ACLK, 20)

    assert dut.u_axi4_lite_master0.M_ARVALID.value == 0
    assert dut.u_axi4_lite_master0.M_AWVALID.value == 0
    assert dut.u_axi4_lite_master0.M_WVALID.value  == 0

@cocotb.test()
async def tc03_single_write(dut):
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut, 2)

    await axi_write(dut, addr=0x05, data=0xDEADBEEF)
    stored = int(dut.u_axi4_lite_slave0.register[5].value)
    assert stored == 0xDEADBEEF, f"Expected 0xDEADBEEF, got 0x{stored:08X}"
    dut._log.info("TC03 PASS — single write OK")


@cocotb.test()
async def tc04_single_read(dut):
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut,1)

    # Pre-seed register 7 directly, bypassing the AXI write channel
    dut.u_axi4_lite_slave0.register[7].value = 0x12345678

    # Wait one clock so the force takes effect in the simulator
    await RisingEdge(dut.ACLK)

    rdata = await axi_read(dut, addr=0x07)
    assert rdata == 0x12345678, \
        f"TC04 FAIL — expected 0x12345678, got 0x{rdata:08X}"
    dut._log.info("TC04 PASS — single read OK")

@cocotb.test()
async def tc05_write_then_readback(dut):
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut,2)
    await axi_write(dut, addr=0x10, data=0xDEADBEEF)
    rdata = await axi_read(dut, addr=0x10)
    assert rdata == 0xDEADBEEF, \
        f"TC04 FAIL — expected 0xDEADBEEF, got 0x{rdata:08X}"
    dut._log.info("TC05 PASS — write and read back OK")

    
@cocotb.test()
async def tc07_write_all_registers(dut):
    """Write a unique value into every register slot and confirm no aliasing."""
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut,2)

    # Write a unique pattern to every slot
    for addr in range(32):
        wdata = 0xA0000000 | addr
        await axi_write(dut, addr, wdata)

    # Verify every slot directly — catches any aliasing between addresses
    for addr in range(32):
        expected = 0xA0000000 | addr
        actual   = int(dut.u_axi4_lite_slave0.register[addr].value)
        assert actual == expected, \
            f"TC07 FAIL — register[{addr}]: expected 0x{expected:08X}, got 0x{actual:08X}"

    dut._log.info("TC07 PASS — all 32 registers written correctly, no aliasing")


@cocotb.test()
async def tc08_read_all_registers(dut):
    """Pre-seed all 32 slots directly, then read each one back via the AXI read path."""
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, unit="ns").start())
    await reset_dut(dut,2)

    # Pre-seed every register directly, bypassing the write channel
    for addr in range(32):
        dut.u_axi4_lite_slave0.register[addr].value = 0xB0000000 | addr

    # Let the forced values settle before starting reads
    await RisingEdge(dut.ACLK)

    # Read each slot back through the full AXI read path and compare
    for addr in range(32):
        expected = 0xB0000000 | addr
        rdata    = await axi_read(dut, addr)
        assert rdata == expected, \
            f"TC08 FAIL — register[{addr}]: expected 0x{expected:08X}, got 0x{rdata:08X}"

    dut._log.info("TC08 PASS — all 32 registers read correctly")


@cocotb.test()
async def tc09_back_to_back_writes(dut):
    """Fire 16 consecutive writes with no gap between transactions."""
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, units="ns").start())
    await reset_dut(dut,2)

    # Write 16 consecutive transactions back-to-back
    for i in range(16):
        await axi_write(dut, addr=i, data=0x11111111 * i)

    # Verify all 16 registers hold the correct values
    for i in range(16):
        expected = (0x11111111 * i) & 0xFFFFFFFF
        actual   = int(dut.u_axi4_lite_slave0.register[i].value)
        assert actual == expected, \
            f"TC09 FAIL — register[{i}]: expected 0x{expected:08X}, got 0x{actual:08X}"

    dut._log.info("TC09 PASS — 16 back-to-back writes completed correctly")


@cocotb.test()
async def tc10_back_to_back_reads(dut):
    """Fire 16 consecutive reads with no gap between transactions."""
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD, units="ns").start())
    await reset_dut(dut,2)

    # Pre-seed 16 registers directly
    for i in range(16):
        dut.u_axi4_lite_slave0.register[i].value = 0xC0000000 | i

    # Let forced values settle
    await RisingEdge(dut.ACLK)

    # Issue 16 consecutive reads back-to-back and verify each one
    for i in range(16):
        expected = 0xC0000000 | i
        rdata    = await axi_read(dut, addr=i)
        assert rdata == expected, \
            f"TC10 FAIL — register[{i}]: expected 0x{expected:08X}, got 0x{rdata:08X}"

    dut._log.info("TC10 PASS — 16 back-to-back reads completed correctly")