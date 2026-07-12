// Code your design here
// Synchronizers
`include "../design/w2rsync.sv"
`include "../design/r2wsync.sv"

// Pointer handlers
`include "../design/write_ptr.sv"
`include "../design/read_ptr.sv"

// Memory
`include "../design/fifo_mem.sv"

module top #(parameter depth=256, data_width=8, ptr_width=9) (
    input  logic                  wclk,
    input  logic                  w_rst_n,
    input  logic                  rclk,
    input  logic                  r_rst_n,
    input  logic                  w_en,
    input  logic                  r_en,
    input  logic [data_width-1:0] data_in,
    output logic [data_width-1:0] data_out,
    output logic                  full,
    output logic                  empty
);

    localparam ADDRSIZE = ptr_width - 1;   // 8

    // Internal signals
    logic [ptr_width-1:0] wptr;
    logic [ptr_width-1:0] rptr;
    logic [ptr_width-1:0] wptr_sync;
    logic [ptr_width-1:0] rptr_sync;
    logic [ptr_width-1:0] waddr;
    logic [ptr_width-1:0] raddr;

    

    // 2-flop synchronizers
    w2rsync #(ptr_width) w2rsync_inst (
        .rclk     (rclk),
        .r_rst_n  (r_rst_n),
        .wptr     (wptr),
        .wptr_sync(wptr_sync)
    );

    r2wsync #(ptr_width) r2wsync_inst (
        .wclk     (wclk),
        .w_rst_n  (w_rst_n),
        .rptr     (rptr),
        .rptr_sync(rptr_sync)
    );

    // Write pointer handler
    write_ptr #(ptr_width) write_ptr_inst (
        .wclk      (wclk),
        .w_rst_n   (w_rst_n),
        .w_en      (w_en),
        .rptr_sync (rptr_sync),
        .waddr     (waddr),
        .wptr      (wptr),
        .full      (full)
    );

    // Read pointer handler
    read_ptr #(ptr_width) read_ptr_inst (
        .rclk      (rclk),
        .r_rst_n   (r_rst_n),
        .r_en      (r_en),
        .wptr_sync (wptr_sync),
        .raddr     (raddr),
        .rptr      (rptr),
        .empty     (empty)
    );

    // FIFO memory
    fifo_mem #(data_width, ptr_width, depth) fifo_mem_inst (
        .wclk    (wclk),
        .rclk    (rclk),
        .r_rst_n (r_rst_n),
        .w_rst_n (w_rst_n),
        .w_en    (w_en),
        .r_en    (r_en),
        .full    (full),
        .empty   (empty),
        .data_in (data_in),
        .waddr   (waddr[ADDRSIZE-1:0]),
        .raddr   (raddr[ADDRSIZE-1:0]),
        .data_out(data_out)
    );

    // Dump waves
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, top);
    end

endmodule