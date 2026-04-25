# AXI4-Lite Verification Environment

A complete verification environment for an AXI4-Lite master/slave design, built using cocotb and pyuvm.

---

## Project Structure

```
AXI4Lite/
├── design/
│   ├── axi4_lite_master.sv   # AXI4-Lite master FSM
│   ├── axi4_lite_slave.sv    # AXI4-Lite slave FSM with 32x32-bit register file
│   └── axi4_lite_top.sv      # Top-level wrapper
├── tb/                        # Directed cocotb testbench
│   ├── Makefile
│   ├── axi4_bfm.py            # BFM helpers for write and read transactions
│   └── axi4_tb_top.py         # 15 directed test cases
└── tb_pyuvm/                  # UVM testbench
    ├── Makefile
    ├── AXI4_utils.py          # BFM with driver and result monitor
    └── AXI4_tb_top.py         # pyuvm environment with scoreboard and coverage
```

---

## tb — Directed Testbench

Contains 15 directed test cases written in cocotb covering:

- Reset correctness and IDLE stability
- Single write and read transactions
- Write then read back
- Full 32-register file write and read
- Back-to-back writes and reads
- Data integrity patterns (all-zeros, all-ones, walking ones)
- Address boundary verification (0x00 and 0x1F)
- Write priority when both write and read are asserted simultaneously
- Mid-transaction reset recovery

**Run:**
```bash
cd tb
make
```

---

## tb_pyuvm — UVM Testbench

A structured pyuvm environment with full UVM methodology:

- Sequence items, sequences, and a sequencer
- Driver backed by a BFM coroutine
- Command monitor observing bus signals independently
- Scoreboard with a Python reference model
- Functional coverage using cocotb-coverage

**Run:**
```bash
cd tb_pyuvm
make
```

---

## Dependencies

```bash
pip install cocotb cocotb-tools pyuvm cocotb-coverage
sudo apt-get install iverilog
```

---

## Known Design Limitations

Two issues identified during RTL review:

**Out-of-bounds address** — the slave uses `register[S_AWADDR]` with no upper bound check. Addresses >= 32 produce undefined behavior. Fix: gate the write with `if (S_AWADDR < 32)` and return a SLVERR response for invalid addresses.

**Combinational latch risk** — both master and slave `always_comb` blocks do not assign `next_state` in every branch, which can infer latches during synthesis. Fix: add `default: next_state = state;` at the top of each `always_comb` block.