from pyuvm import uvm_agent, uvm_sequencer, uvm_analysis_port
from .write_driver  import FifoWriteDriver
from .write_monitor import FifoWriteMonitor
 
 
class FifoWriteAgent(uvm_agent):
 
    def build_phase(self):
        self.seqr    = uvm_sequencer("write_seqr", self)
        self.driver  = FifoWriteDriver("write_driver", self)
        self.monitor = FifoWriteMonitor("write_monitor", self)
        self.ap      = uvm_analysis_port("write_agent_ap", self)
 
    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.monitor.ap.connect(self.ap)