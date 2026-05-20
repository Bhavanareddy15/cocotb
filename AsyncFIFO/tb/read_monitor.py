import cocotb
from cocotb.triggers import RisingEdge, Timer
from pyuvm import uvm_component, uvm_analysis_port
from async_fifo_seq_item import FifoReadItem
 
 
class FifoReadMonitor(uvm_component):
 
    def build_phase(self):
        self.dut = cocotb.top
        self.ap  = uvm_analysis_port("read_ap", self)
 
    async def run_phase(self):
        self.logger.info("FifoReadMonitor started")
        while True:
            await RisingEdge(self.dut.rclk)
            await Timer(1, "step")
 
            r_en  = int(self.dut.r_en.value)
            empty = int(self.dut.empty.value)
 
            if r_en and not empty:
                item          = FifoReadItem("rmon_item")
                item.r_en     = 1
                item.empty    = 0
                item.data_out = int(self.dut.data_out.value)
                self.ap.write(item)
                self.logger.debug(f"ReadMonitor: {item}")