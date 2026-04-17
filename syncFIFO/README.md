# syncFIFO

A synchronous FIFO design verified using cocotb.

---

## Project Structure

```
syncFIFO/
├── design.sv        # RTL design (fifo_sync module, depth=4, width=8)
├── fifo_model.py    # Python reference model
├── makefile         # Makefile flow entry point
├── test_FIFO.py     # Testbench + runner
└── README.md
```

---

## Prerequisites

```bash
pip install cocotb cocotb-tools pytest
sudo apt install iverilog      # Ubuntu / WSL
```

---

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Depth     | 4     |
| Width     | 8 bits |
| Type      | Synchronous, registered output |
| Reset     | Synchronous, active high |

---

## Test Cases

### `fifo_basic_test`
Writes a single value (`0xAB`) and reads it back. Checks that the DUT output matches the model and that the `full` and `empty` flags are correct after the operation.

### `fifo_full_test`
Writes 4 items to fill the FIFO completely. Verifies the `full` flag asserts and `empty` stays low. Then attempts an extra write while full and confirms the FIFO is not corrupted.

### `fifo_empty_test`
Fills the FIFO then drains it completely, comparing each read against the model. Verifies the `empty` flag asserts after the last read. Then attempts an extra read while empty and confirms `dout` does not change.

### `fifo_concurrent_test`
Asserts `wr_en` and `rd_en` simultaneously in the same clock cycle. Verifies that the item count stays stable (net zero change) and that the correct data is read out and written in.

### `fifo_reset_midop_test`
Writes 3 items into the FIFO, then asserts reset mid-operation. Verifies that after reset, `empty` is high, `full` is low, and `dout` is cleared to zero.

### `fifo_random_test`
Runs 200 cycles of random interleaved reads, writes, and idle cycles. Every operation is mirrored on the Python model and compared against the DUT. `full` and `empty` flags are checked on every cycle.

---

## Running the Tests

### All tests — using Make

From inside the `syncFIFO/` directory:

```bash
make
```

This compiles `design.sv` with Icarus Verilog and runs all `@cocotb.test()` functions in `test_FIFO.py` in the order they are defined.

To clean build artifacts and re-run:

```bash
make clean && make
```

---

### All tests — using the Python runner

```bash
python test_FIFO.py
```

Or via pytest:

```bash
pytest test_FIFO.py
```

---

### Running a single specific test

cocotb supports filtering by test name using the `COCOTB_TEST_FILTER` environment variable.

**Via Make:**

```bash
make COCOTB_TEST_FILTER=fifo_basic_test
make COCOTB_TEST_FILTER=fifo_full_test
make COCOTB_TEST_FILTER=fifo_empty_test
make COCOTB_TEST_FILTER=fifo_concurrent_test
make COCOTB_TEST_FILTER=fifo_reset_midop_test
make COCOTB_TEST_FILTER=fifo_random_test
```

**Via Python runner / pytest:**

```bash
pytest test_FIFO.py::test_fifo_runner -k fifo_basic_test
```

---

## Expected Output

A full passing run looks like:

```
<img width="1057" height="232" alt="image" src="https://github.com/user-attachments/assets/c0f35034-ea0f-498d-bd74-acf58e8ed4ca" />

```

---

## How the Model Works

`fifo_model.py` implements a Python list-based FIFO that mirrors the DUT:

```python
model = FifoModel(depth=4)
model.write(data)    # mirrors wr_en
model.read()         # mirrors rd_en, returns expected dout
model.full()         # mirrors full flag
model.empty()        # mirrors empty flag
```

Every test drives the same data into both the DUT and the model, then asserts that outputs and flags match. Any mismatch fails the test immediately with a message showing both the DUT value and the expected model value.
```

---
