# Synchronous FIFO Cocotb Testbench

## Project Structure

```
syncFIFO/
├── design.sv       # RTL design (fifo_sync module)
├── makefile        # Makefile flow
├── test_FIFO.py    # Testbench + runner
└── fifo_model.py   # (optional) Python reference model
```

---

## Prerequisites

Install cocotb and Icarus Verilog:

```bash
pip install cocotb cocotb-tools
sudo apt install iverilog      # Ubuntu/WSL
```

Verify both are available:

```bash
cocotb-config --version
iverilog -V
```

---

## Running the Tests

There are two ways to run the testbench.

---

### 1. Using Make (recommended)

This is the standard cocotb flow. Run from inside the `syncFIFO/` directory:

```bash
make
```

To choose a different simulator:

```bash
make SIM=verilator
```

To clean build artifacts and force a fresh run:

```bash
make clean
make
```

**How it works:**

```
make → iverilog compiles design.sv → vvp loads cocotb → cocotb imports test_FIFO.py
```

The `makefile` controls:
- Which simulator is used (`SIM`, defaults to `icarus`)
- Which RTL file is compiled (`VERILOG_SOURCES`)
- Which module is the top level (`COCOTB_TOPLEVEL`)
- Which Python test file is loaded (`COCOTB_TEST_MODULES`)

---

### 2. Running the File Directly

The `test_FIFO.py` file contains a `test_fifo_runner()` function at the bottom that replicates the Makefile flow in pure Python. Run it with:

```bash
python test_FIFO.py
```

Or via pytest (install with `pip install pytest`):

```bash
pytest test_FIFO.py
```

**How it works:**

```
python test_FIFO.py → test_fifo_runner() → runner.build() → runner.test()
```

The runner inside `test_FIFO.py` controls:
- Source files and top-level module
- Timescale (`1ns / 1ps`)
- Which test module to load

---

## Expected Output

A passing run looks like:

```
** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
** test_FIFO.fifo_basic_test      PASS           5.00           0.01        335.58  **
** TESTS=1 PASS=1 FAIL=0 SKIP=0                  5.00           0.02        260.31  **
```

---
