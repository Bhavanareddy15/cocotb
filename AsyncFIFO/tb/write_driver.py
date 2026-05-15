import cocotb
from cocotb.triggers import RisingEdge, Timer
from pyuvm import uvm_driver

class FifoWriteDriver(uvm_driver):
 
    def build_phase(self):
        self.dut = cocotb.top
 
    async def run_phase(self):
        self.logger.info("FifoWriteDriver started")
        self.dut.w_en.value    = 0
        self.dut.data_in.value = 0
 
        while True:
            item = await self.seq_item_port.get_next_item()
            await RisingEdge(self.dut.wclk)
            self.dut.w_en.value    = int(item.w_en)
            self.dut.data_in.value = int(item.data_in)
            await RisingEdge(self.dut.wclk)   # hold 1 wclk cycle
            self.dut.w_en.value = 0
            self.seq_item_port.item_done()