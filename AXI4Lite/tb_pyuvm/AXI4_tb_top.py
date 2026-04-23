from cocotb.triggers import Join, Combine
from pyuvm import *
import random
import cocotb
import pyuvm

from AXI4_utils import axi4_bfm

class AXIWriteSeqItem(uvm_sequence_item):
    def __init__(self, name, addr, data):
        super().__init__(name)
        self.addr   = addr
        self.data   = data

    def randomize(self):
        self.addr = random.randint(0, 31)
        self.data = random.randint(0, 0xFFFFFFFF)

    def __str__(self):
        return f"{self.get_name()} : WRITE addr=0x{self.addr:02X} data=0x{self.data:08X}"


class AXIReadSeqItem(uvm_sequence_item):
    def __init__(self, name, addr):
        super().__init__(name)
        self.addr   = addr
        self.result = None    # populated by driver after read completes

    def randomize(self):
        self.addr = random.randint(0, 31)

    def __str__(self):
        return f"{self.get_name()} : READ addr=0x{self.addr:02X} result=0x{self.result:08X}"