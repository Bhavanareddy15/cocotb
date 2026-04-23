import logging

import cocotb
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import FallingEdge

from pyuvm import Singleton

class axi4_bfm(metaclass= Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driv_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def reset_dut(self):
        
