from pyuvm import uvm_agent, uvm_sequencer, uvm_analysis_port
from read_driver  import FifoReadDriver
from read_monitor import FifoReadMonitor
 
 
class FifoReadAgent(uvm_agent):
 
    def build_phase(self):
        self.seqr    = uvm_sequencer("read_seqr", self)
        self.driver  = FifoReadDriver("read_driver", self)
        self.monitor = FifoReadMonitor("read_monitor", self)
        self.ap      = uvm_analysis_port("read_agent_ap", self)
 
    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.monitor.ap.connect(self.ap)