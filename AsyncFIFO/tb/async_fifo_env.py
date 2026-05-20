from pyuvm import uvm_env
from write_agent import FifoWriteAgent
from read_agent  import FifoReadAgent
#from scoreboard  import FifoScoreboard
#from coverage    import FifoCoverage
 
 
class FifoEnv(uvm_env):
 
    def build_phase(self):
        self.write_agent = FifoWriteAgent("write_agent", self)
        self.read_agent  = FifoReadAgent("read_agent",   self)
        self.scoreboard  = FifoScoreboard("scoreboard",  self)
        self.coverage    = FifoCoverage("coverage",      self)
 
    def connect_phase(self):
        # Write monitor → scoreboard write port
        self.write_agent.ap.connect(self.scoreboard.write_export)
        # Read  monitor → scoreboard read port
        self.read_agent.ap.connect(self.scoreboard.read_export)