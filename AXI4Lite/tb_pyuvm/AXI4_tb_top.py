from pyuvm import *
import random
import cocotb
import pyuvm
from cocotb.clock import Clock

from AXI4_utils import axi4_bfm, get_int

from AXI4_model import AXI4LiteModel

CLK_PERIOD = 10  # ns


# ---------------------------------------------------------------------------
# Sequence items
# ---------------------------------------------------------------------------
class AXIWriteSeqItem(uvm_sequence_item):
    def __init__(self, name, addr=None, data=None):
        super().__init__(name)
        self.addr = addr
        self.data = data

    def randomize(self):
        self.addr = random.randint(0, 31)
        self.data = random.randint(0, 0xFFFFFFFF)

    def __str__(self):
        return f"{self.get_name()} : WRITE addr=0x{self.addr:02X} data=0x{self.data:08X}"


class AXIReadSeqItem(uvm_sequence_item):
    def __init__(self, name, addr=None):
        super().__init__(name)
        self.addr   = addr
        self.result = None

    def randomize(self):
        self.addr = random.randint(0, 31)

    def __str__(self):
        result_str = f"0x{self.result:08X}" if self.result is not None else "pending"
        return f"{self.get_name()} : READ addr=0x{self.addr:02X} result={result_str}"


# ---------------------------------------------------------------------------
# Sequences
# ---------------------------------------------------------------------------
class WriteSeq(uvm_sequence):
    async def body(self):
        item = AXIWriteSeqItem("write_item")
        await self.start_item(item)
        item.randomize()
        await self.finish_item(item)


class ReadSeq(uvm_sequence):
    async def body(self):
        item = AXIReadSeqItem("read_item")
        await self.start_item(item)
        item.randomize()
        await self.finish_item(item)


class WriteReadBackSeq(uvm_sequence):
    """Write to a specific address then immediately read it back."""
    def __init__(self, name, addr, data):
        super().__init__(name)
        self.addr = addr
        self.data = data

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")

        # Write
        write_item = AXIWriteSeqItem("write", self.addr, self.data)
        await self.start_item(write_item)
        await self.finish_item(write_item)

        # Read back same address
        read_item = AXIReadSeqItem("read", self.addr)
        await self.start_item(read_item)
        await self.finish_item(read_item)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
class Driver(uvm_driver):

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = axi4_bfm()

    async def launch_tb(self):
        await self.bfm.reset_dut()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            item = await self.seq_item_port.get_next_item()

            if isinstance(item, AXIWriteSeqItem):
                await self.bfm.send_write(item.addr, item.data)
            elif isinstance(item, AXIReadSeqItem):
                await self.bfm.send_read(item.addr)

            # Wait for result monitor to confirm the transaction completed
            result = await self.bfm.get_result()
            (txn_type, addr, data) = result

            # Populate result back onto read item
            if isinstance(item, AXIReadSeqItem):
                item.result = data

            # Print result so we can confirm manually
            if txn_type == "write":
                self.logger.info(
                    f"WRITE completed — addr=0x{addr:02X} data=0x{data:08X}"
                )
            elif txn_type == "read":
                self.logger.info(
                    f"READ  completed — addr=0x{addr:02X} result=0x{data:08X}"
                )

            self.ap.write(result)
            self.seq_item_port.item_done()

# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------

class Monitor(uvm_monitor):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm =  axi4_bfm()
    
    async def run_phase(self):
        while True:
            datum = await self.bfm.get_cmd()
            self.ap.write(datum)
# ---------------------------------------------------------------------------
# Scoreboard 
# ---------------------------------------------------------------------------

class Scoreboard(uvm_scoreboard):
    def build_phase(self):
        self.cmd_fifo    = uvm_tlm_analysis_fifo("cmd_fifo",    self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)

        self.cmd_get_port    = uvm_get_port("cmd_get_port",    self)
        self.result_get_port = uvm_get_port("result_get_port", self)

        self.cmd_export    = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

        self.model = AXI4LiteModel()

    def connect_phase(self):
        self.cmd_get_port.connect(self.cmd_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        # comparison logic here
        passed = True
        while self.result_get_port.can_get():
            _, actual = self.result_get_port.try_get()   # ← from result_fifo
            cmd_ok , cmd    = self.cmd_get_port.try_get()       # ← from cmd_fifo

            if not cmd_ok:
                self.logger.critical("Result has no matching command")
                continue

            (txn_type, addr, data) =  cmd

            if txn_type == "write":
                self.model.write(addr, data)

            elif txn_type == "read":
                (_, _, actual_result) = actual
                predicted = self.model.read(addr)
                if predicted == actual_result:
                    self.logger.info(
                        f"PASSED READ addr=0x{addr:02X} "
                        f"expected=0x{predicted:08X} got=0x{actual_result:08X}"
                    )
                else:
                    self.logger.error(
                        f"FAILED READ addr=0x{addr:02X} "
                        f"expected=0x{predicted:08X} got=0x{actual_result:08X}"
                    )
                    passed = False
        assert passed
                



# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
class AXIEnv(uvm_env):

    def build_phase(self):
        self.seqr   = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver.create("driver", self)
        self.cmd_mon    = Monitor.create("cmd_mon", self)
        self.scoreboard = Scoreboard("scoreboard", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)      # cmd flow
        self.driver.ap.connect(self.scoreboard.result_export)    # result flow


# ---------------------------------------------------------------------------
# Test — write then read back 4 addresses and print results
# ---------------------------------------------------------------------------
@pyuvm.test()
class WriteReadBackTest(uvm_test):
    """Write then immediately read back — print results for manual confirmation."""

    def build_phase(self):
        self.env = AXIEnv("env", self)

    def start_of_simulation_phase(self):
        cocotb.start_soon(
            Clock(cocotb.top.ACLK, CLK_PERIOD, units="ns").start()
        )

    async def run_phase(self):
        self.raise_objection()
        seqr = ConfigDB().get(None, "", "SEQR")

        # Use a small number of addresses for easy manual checking
        test_vectors = [
            (0x00, 0xDEADBEEF),
            (0x01, 0xCAFEBABE),
            (0x1F, 0x12345678),
            (0x0A, 0xA5A5A5A5),
        ]

        for addr, data in test_vectors:
            self.logger.info(f"--- Sending WRITE addr=0x{addr:02X} data=0x{data:08X} ---")
            await WriteReadBackSeq("wrb", addr, data).start(seqr)

        self.drop_objection()