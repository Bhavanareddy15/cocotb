import os
from pathlib import Path
from cocotb.runner import get_runner
 
 
def test_axi4lite_runner():
    """Simulate axi4_lite_top using the Python runner.
 
    This file can be run directly or via pytest discovery.
    """
    sim = os.getenv("SIM", "icarus")
 
    # tb/ is the folder this file lives in
    tb_path   = Path(__file__).resolve().parent
    # design/ is one level up from tb/
    proj_path = tb_path.parent
 
    sources = [
        proj_path / "design" / "axi4_lite_master.sv",
        proj_path / "design" / "axi4_lite_slave.sv",
        proj_path / "design" / "axi4_lite_top.sv",
    ]
 
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="axi4_lite_top",
        always=True,
        build_args=["-g2012"],
        timescale=("1ns", "1ps"),
    )
    runner.test(
        hdl_toplevel="axi4_lite_top",
        test_module="axi4_tb_top",   # maps to tb/axi4_tb_top.py
    )
 
 
if __name__ == "__main__":
    test_axi4lite_runner()