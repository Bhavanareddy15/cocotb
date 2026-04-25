# AXI4-Lite Verification Testbench

A cocotb-based functional verification suite for an AXI4-Lite master/slave design.

---

## Project Structure

```
AXI4Lite/
├── design/
│   ├── axi4_lite_master.sv   # AXI4-Lite master FSM
│   ├── axi4_lite_slave.sv    # AXI4-Lite slave FSM with 32x32-bit register file
│   └── axi4_lite_top.sv      # Top-level wrapper connecting master and slave
└── tb/
    ├── axi4_bfm.py           # Bus functional model — shared BFM helpers
    ├── axi4_tb_top.py        # Main test module containing all test cases
    ├── test_runner.py        # Python runner (pytest / direct execution)
    └── Makefile              # Makefile for cocotb simulation
```

---

## Dependencies

| Tool | Version tested |
|---|---|
| Python | 3.12 |
| cocotb | 2.0.1 |
| cocotb-tools | latest |
| Icarus Verilog | 12.0 |

Install Python dependencies into a virtual environment:

```bash
python -m venv cocotb-venv
source cocotb-venv/bin/activate
pip install cocotb cocotb-tools
```

---

## Running the Tests

### Using Make (from inside the `tb/` directory)

```bash
cd AXI4Lite/tb
make              # runs all tests with Icarus Verilog
make SIM=questa   # swap simulator
make clean        # remove build artefacts
```

### Using the Python Runner (from inside the `tb/` directory)

```bash
cd AXI4Lite/tb
python test_runner.py       # run directly
pytest test_runner.py -v    # run via pytest with verbose output
```

---

## Design Notes

**Register file:** The slave contains a 32-element array of 32-bit registers (`register[0]` to `register[31]`). The address passed by the master is used directly as the array index.

**R_data port:** `axi4_lite_top` exposes a single output port `R_data [31:0]` which carries the read data from the slave back to the outside world. All other AXI channel signals are internal wires connecting the master and slave instances.

**WSTRB:** The master hardwires `M_WSTRB` to `4'b1111`, meaning all four byte lanes are always written on every write transaction.

**BRESP / RRESP:** Both response signals are hardwired to `2'b00` (OKAY) in the slave. There is no DECERR logic for out-of-range addresses.

**Write priority:** When `write_s` and `read_s` are asserted simultaneously, the master FSM always enters the write path first.

---

## Test Cases

### Sanity

| ID | Name | Description |
|---|---|---|
| TC01 | Reset correctness | Verify both FSMs land in IDLE and all 32 registers are zero after reset |
| TC02 | IDLE stability | Confirm no AXI channel signals toggle when no start signal is driven |

### Single Transaction

| ID | Name | Description |
|---|---|---|
| TC03 | Single write | Write one value to one address and verify it is stored in the slave |
| TC04 | Single read | Pre-seed a register directly, read it back via the AXI read path |
| TC05 | Write then read back | Write via master, read back via master, compare at the `R_data` port |

### Full Register File

| ID | Name | Description |
|---|---|---|
| TC07 | Write all 32 registers | Drive a unique value into every slot and confirm no aliasing |
| TC08 | Read all 32 registers | Pre-seed all slots, read each one back via the AXI read path |

### Sequential Transactions

| ID | Name | Description |
|---|---|---|
| TC09 | Back-to-back writes | 16 consecutive writes with no gap between transactions |
| TC10 | Back-to-back reads | Pre-seed 16 registers, issue 16 consecutive reads |

### Data Integrity

| ID | Name | Description |
|---|---|---|
| TC11 | Data patterns | Write all-zeros, all-ones, and walking-ones patterns, read each back |
| TC12 | Address boundaries | Verify correct behavior at the lowest (0x00) and highest valid (0x1F) address |

### Corner Cases

| ID | Name | Description |
|---|---|---|
| TC13 | Write priority | Assert both `write_s` and `read_s` simultaneously, confirm write wins |
| TC14 | Reset during write | Deassert `ARESETN` mid write-transaction, verify FSMs return to IDLE cleanly |
| TC15 | Reset during read | Deassert `ARESETN` mid read-transaction, verify FSMs return to IDLE cleanly |

---

## BFM Helper Reference (`axi4_bfm.py`)

```python
await reset_dut(dut, cycles=5)
# Asserts active-low reset for `cycles` clock edges then releases it.

await axi_write(dut, addr, data, timeout=50)
# Drives a complete AXI4-Lite write transaction (AW + W + B channels).
# Waits for the master FSM to return to IDLE before returning.

rdata = await axi_read(dut, addr, timeout=50)
# Drives a complete AXI4-Lite read transaction (AR + R channels).
# Latches S_RDATA while S_RVALID is high, returns the integer value.
```

---

## Known Design Limitations

**Out-of-bounds address:** The slave uses `register[S_AWADDR]` with the full 32-bit address as an array index into a 32-element array. Addresses ≥ 32 cause undefined behavior in simulation. The fix is to gate the write with `if (S_AWADDR < 32)` and optionally return a DECERR response.

**Combinational latch risk:** Both master and slave `always_comb` blocks do not assign `next_state` in every branch. This can infer latches during synthesis. The fix is to add `default: next_state = state;` at the top of each `always_comb` block.
