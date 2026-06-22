import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

import pyuvm
from pyuvm import *
import random

class FifoWriteItem(uvm_sequence_item):
    def __init__(self, name="FifoWriteItem"):
        super().__init__(name)
        self.data_in= 0
        self.w_en=0
        
    def randomize(self):
        self.data_in = random.randint(0,255)
        self.w_en    = random.choices([1, 0], weights=[80, 20])[0]  # 80% chance of write

    def do_copy(self, rhs):
        self.data_in = rhs.data_in
        self.w_en    = rhs.w_en

    def __str__(self):
        return (f"FifoWriteItem: w_en={self.w_en}  "
                f"data_in=0x{self.data_in:02X}")
    
class FifoReadItem(uvm_sequence_item):
    def __init__(self, name="FifoReadItem" ):
        super().__init__(name)
        self.r_en= 0
        self.data_out = 0
        self.empty    = 1
    
    def randomize(self):
        self.r_en = random.choices([1, 0], weights=[80, 20])[0]  # 80% chance of read
    
    def __str__(self):
        return (f"FifoReadItem: r_en={self.r_en}  "
                f"data_out=0x{self.data_out:02X}  empty={self.empty}")
 