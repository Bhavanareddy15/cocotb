import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


CLK_PERIOD = 10  # ns

async def reset_dut(dut, cycles):
    dut.ARESETN.value = 0
    dut.read_s.value = 0
    dut.write_s.value = 0
    dut.address.value = 0
    dut.W_data.value = 0

    for _ in range(cycles):
        await RisingEdge(dut.ACLK)
    
    dut.ARESETN.value = 1
    await RisingEdge(dut.ACLK)


async def axi_write(dut, addr, data, timeout=50):
    """Drive write_s for one cycle and wait for WRESP handshake."""
    await RisingEdge(dut.ACLK)
    dut.address.value = addr
    dut.W_data.value  = data
    dut.write_s.value = 1
    await RisingEdge(dut.ACLK)
    dut.write_s.value = 0
    await RisingEdge(dut.ACLK)  
    # Wait for master to return to IDLE (BVALID+BREADY)
    for _ in range(timeout):
        await RisingEdge(dut.ACLK)
        # Master is back in IDLE when M_AWVALID deasserts after WRESP
        if dut.u_axi4_lite_master0.state.value == 0:  # IDLE
            return
    raise AssertionError(f"Write timeout addr=0x{addr:08X}")

async def axi_read(dut, addr, timeout=50):
    """Drive read_s for one cycle and return sampled read data."""
    await RisingEdge(dut.ACLK)
    dut.address.value = addr
    dut.read_s.value  = 1
    await RisingEdge(dut.ACLK)
    dut.read_s.value  = 0
    await RisingEdge(dut.ACLK) 

    rdata = 0
    for _ in range(timeout):
        await RisingEdge(dut.ACLK)
        if int(dut.u_axi4_lite_slave0.S_RVALID.value) == 1:
            rdata = int(dut.R_data.value)          # latch the value here
        if dut.u_axi4_lite_master0.state.value == 0:  # IDLE
            return rdata
    raise AssertionError(f"Read timeout addr=0x{addr:08X}")



    
    
