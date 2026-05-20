import cocotb
from cocotb.triggers import RisingEdge, Timer
from pyuvm import uvm_component, uvm_analysis_port
from async_fifo_seq_item import FifoWriteItem
 
 
class FifoWriteMonitor(uvm_component):
 
    def build_phase(self):
        self.dut = cocotb.top
        self.ap  = uvm_analysis_port("write_ap", self)
 
    async def run_phase(self):
        self.logger.info("FifoWriteMonitor started")
        while True:
            await RisingEdge(self.dut.wclk)
            await Timer(1, "step")          # sample after clock edge (preponed)
 
            w_en = int(self.dut.w_en.value)
            full = int(self.dut.full.value)
 
            if w_en and not full:
                item         = FifoWriteItem("wmon_item")
                item.w_en    = 1
                item.data_in = int(self.dut.data_in.value)
                self.ap.write(item)
                self.logger.debug(f"WriteMonitor: {item}")