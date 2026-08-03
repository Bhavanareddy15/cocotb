# fifo_config.py
# Single source of truth for FIFO capacity, shared by tests and scoreboard.
# Must match the RTL: ptr_width=9 -> ADDRSIZE=8 -> 2^8 = 256
FIFO_DEPTH = 256