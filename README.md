# cocotb

A collection of hardware designs and their cocotb testbenches, built as a learning reference for simulation-based verification using Python.

---

Each subdirectory is a self-contained project with its own RTL design, testbench, and makefile.

---

## Prerequisites

**Python packages:**

```bash
pip install cocotb cocotb-tools pytest
```

**Simulator — Icarus Verilog:**

```bash
# Ubuntu / WSL
sudo apt install iverilog

# macOS
brew install icarus-verilog
```

**Verify the install:**

```bash
cocotb-config --version
iverilog -V
```

---

## Running a Testbench

Navigate into any project folder and run `make`:

```bash
cd syncFIFO
make
```

Or run the testbench directly as a Python script:

```bash
python test_FIFO.py
```

Both methods produce the same result. See the README inside each project folder for project-specific instructions.

---

## Projects

| Folder | Design | Description |
|---|---|---|
| `simple_adder` | Combinational adder | Basic cocotb setup with combinational logic and a timer-based test |
| `syncFIFO` | Synchronous FIFO | Clocked design with reset, write/read coroutines, and a Python reference model |

---

## Tools Used

- **[cocotb](https://www.cocotb.org/)** — Python-based hardware verification framework
- **[Icarus Verilog](http://iverilog.icarus.com/)** — Open source Verilog/SystemVerilog simulator
- **[pytest](https://pytest.org/)** — Test runner for the Python-based runner flow
