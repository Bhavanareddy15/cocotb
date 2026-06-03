import cocotb
from cocotb.triggers import RisingEdge, Timer
from pyuvm import uvm_component, uvm_tlm_analysis_fifo

from fifo_model import FifoModel

class FifoScoreboard(uvm_component):
    def build_phase(self):
        self.write_fifo = uvm_tlm_analysis_fifo("write_fifo", self)
        self.read_fifo  = uvm_tlm_analysis_fifo("read_fifo", self)
        self.ref_model  = FifoModel(depth=16)  # match your RTL depth

    async def run_phase(self):
        self.logger.info("Scoreboard started")
        cocotb.start_soon(self.write_handler())
        cocotb.start_soon(self.read_handler())

    async def write_handler(self):
        while True:
            write_item = await self.write_fifo.get()
            self.ref_model.write(write_item.data_in)
            self.logger.debug(f"Model write: 0x{write_item.data_in:02X}")

    async def read_handler(self):
        while True:
            read_item = await self.read_fifo.get()
            expected  = self.ref_model.read()

            if expected is None:
                self.logger.error("FAIL: read from empty model")
            elif read_item.data_out == expected:
                self.logger.info(f"PASS: expected 0x{expected:02X} got 0x{read_item.data_out:02X}")
            else:
                self.logger.error(f"FAIL: expected 0x{expected:02X} got 0x{read_item.data_out:02X}")
                