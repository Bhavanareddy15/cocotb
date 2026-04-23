import cocotb
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import RisingEdge
from pyuvm import Singleton


def get_int(signal):
    try:
        return int(signal.value)
    except ValueError:
        return 0


class axi4_bfm(metaclass=Singleton):
    def __init__(self):
        self.dut              = cocotb.top
        self.driv_queue       = Queue(maxsize=1)
        self.result_mon_queue = Queue(maxsize=0)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    async def reset_dut(self):
        self.dut.ARESETN.value = 0
        self.dut.read_s.value  = 0
        self.dut.write_s.value = 0
        self.dut.address.value = 0
        self.dut.W_data.value  = 0
        await RisingEdge(self.dut.ACLK)
        await RisingEdge(self.dut.ACLK)
        self.dut.ARESETN.value = 1
        await RisingEdge(self.dut.ACLK)

    # ------------------------------------------------------------------
    # Send helpers called by Driver
    # ------------------------------------------------------------------
    async def send_write(self, addr, data):
        await self.driv_queue.put(("write", addr, data))

    async def send_read(self, addr):
        await self.driv_queue.put(("read", addr, 0))

    async def get_result(self):
        return await self.result_mon_queue.get()

    # ------------------------------------------------------------------
    # Driver BFM
    # ------------------------------------------------------------------
    async def driver_bfm(self):
        # Initialise outputs — do NOT touch ARESETN here, reset_dut owns it
        self.dut.write_s.value = 0
        self.dut.read_s.value  = 0
        self.dut.address.value = 0
        self.dut.W_data.value  = 0

        while True:
            await RisingEdge(self.dut.ACLK)

            # Only pick a new item when the master FSM is in IDLE (state=0)
            if get_int(self.dut.u_axi4_lite_master0.state) == 0:
                try:
                    (txn_type, addr, data) = self.driv_queue.get_nowait()

                    self.dut.address.value = addr
                    self.dut.W_data.value  = data

                    if txn_type == "write":
                        self.dut.write_s.value = 1
                        self.dut.read_s.value  = 0
                    else:
                        self.dut.read_s.value  = 1
                        self.dut.write_s.value = 0

                    # Deassert after one cycle — signal is registered in RTL
                    await RisingEdge(self.dut.ACLK)
                    self.dut.write_s.value = 0
                    self.dut.read_s.value  = 0

                except QueueEmpty:
                    pass

    # ------------------------------------------------------------------
    # Result monitor BFM
    # ------------------------------------------------------------------
    async def result_mon_bfm(self):
        """
        Detects when the master FSM returns to IDLE and pushes a result
        tuple (txn_type, addr, data) onto result_mon_queue.

        Address is latched when FSM leaves IDLE so it is not lost by
        the time the transaction completes.
        """
        prev_state  = 0
        rdata_latch = 0
        addr_latch  = 0

        while True:
            await RisingEdge(self.dut.ACLK)

            state = get_int(self.dut.u_axi4_lite_master0.state)

            # Latch address the cycle the FSM first leaves IDLE
            if prev_state == 0 and state != 0:
                addr_latch = get_int(self.dut.address)

            # Latch read data while slave RVALID is high (RDATA state = 4)
            if state == 4:
                if get_int(self.dut.u_axi4_lite_slave0.S_RVALID) == 1:
                    rdata_latch = get_int(self.dut.R_data)

            # Detect FSM returning to IDLE — transaction is complete
            if prev_state != 0 and state == 0:
                if prev_state == 2:    # WRESP__CHANNEL — write completed
                    result = ("write", addr_latch, 0)
                elif prev_state == 4:  # RDATA__CHANNEL — read completed
                    result = ("read", addr_latch, rdata_latch)
                else:
                    result = None

                if result is not None:
                    self.result_mon_queue.put_nowait(result)

            prev_state = state

    # ------------------------------------------------------------------
    # Start all background BFMs
    # ------------------------------------------------------------------
    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.result_mon_bfm())