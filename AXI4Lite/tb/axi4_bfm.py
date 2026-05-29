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
    # --- Wait for Write-Response handshake (BVALID & BREADY) ---
    for _ in range(timeout):
        await RisingEdge(dut.ACLK)
        if int(dut.BVALID.value) == 1 and int(dut.BREADY.value) == 1:
            bresp = int(dut.BRESP.value)
            assert bresp == 0b00, (
                f"Write to 0x{addr:08X} returned non-OKAY response: {bresp:#04b}"
            )
            return
    raise AssertionError(f"Write timeout — no BVALID/BREADY after {timeout} cycles "
                         f"(addr=0x{addr:08X})")

async def axi_read(dut, addr, timeout=50):
    """Drive read_s for one cycle and return sampled read data."""
    await RisingEdge(dut.ACLK)
    dut.address.value = addr
    dut.read_s.value  = 1
    await RisingEdge(dut.ACLK)
    dut.read_s.value  = 0
    await RisingEdge(dut.ACLK) 

    #rdata = 0
    # --- Wait for Read-Data handshake (RVALID & RREADY) ---
    for _ in range(timeout):
        await RisingEdge(dut.ACLK)
        if int(dut.RVALID.value) == 1 and int(dut.RREADY.value) == 1:
            rresp = int(dut.RRESP.value)
            assert rresp == 0b00, (
                f"Read from 0x{addr:08X} returned non-OKAY response: {rresp:#04b}"
            )
            return int(dut.R_data.value)
    raise AssertionError(f"Read timeout — no RVALID/RREADY after {timeout} cycles "
                         f"(addr=0x{addr:08X})")



    
    
