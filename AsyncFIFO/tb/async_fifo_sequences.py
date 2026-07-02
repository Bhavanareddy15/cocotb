import pyuvm
from pyuvm import *
from async_fifo_seq_item import FifoWriteItem, FifoReadItem
import random


class FifoWriteSeq(uvm_sequence):
    def __init__(self, name="FifoWriteSeq"):
        super().__init__(name)
        self.count=20

    async def body(self):
        for _ in range(self.count):
            item = FifoWriteItem("FifoWriteItem")
            item.randomize()
            item.w_en = 1          # force writes enabled for basic test
            await self.start_item(item)
            await self.finish_item(item)


class FifoReadSeq(uvm_sequence):
    def __init__(self, name="FifoReadSeq"):
        super().__init__(name)
        self.count=20

    async def body(self):
        for _ in range(self.count):
            item = FifoReadItem("FifoReadItem")
            item.r_en = 1          # force writes enabled for basic test
            await self.start_item(item)
            await self.finish_item(item)

class FifoFillSeq(FifoWriteSeq):
    async def body(self):
        for i in range(self.count):
            item = FifoWriteItem("item")
            await self.start_item(item)
            # ← modify here, after lock acquired, before driver gets it
            item.w_en    = 1
            item.data_in = i & 0xFF
            await self.finish_item(item)