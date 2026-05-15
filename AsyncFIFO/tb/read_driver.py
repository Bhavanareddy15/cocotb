import cocotb
from cocotb.triggers import RisingEdge
from pyuvm import uvm_driver
 
 
class FifoReadDriver(uvm_driver):
 
    def build_phase(self):
        self.dut = cocotb.top
 
    async def run_phase(self):
        self.logger.info("FifoReadDriver started")
        self.dut.r_en.value = 0
 
        while True:
            item = await self.seq_item_port.get_next_item()
            await RisingEdge(self.dut.rclk)
            self.dut.r_en.value = int(item.r_en)
            await RisingEdge(self.dut.rclk)   # hold 1 rclk cycle
            self.dut.r_en.value = 0
            self.seq_item_port.item_done()