module axi4_lite_top #(
    parameter DATA_WIDTH = 32,
    parameter ADDRESS    = 32
)(
    input                       ACLK,
    input                       ARESETN,
    input                       read_s,
    input                       write_s,
    input  [ADDRESS-1:0]        address,
    input  [DATA_WIDTH-1:0]     W_data,

    // Read channel outputs
    output [DATA_WIDTH-1:0]     R_data,
    output                      RVALID,
    output                      RREADY,
    output [1:0]                RRESP,

    // Write response channel outputs
    output                      BVALID,
    output                      BREADY,
    output [1:0]                BRESP
);

    // Read address channel
    logic                   M_ARVALID, S_ARREADY;
    logic  [ADDRESS-1:0]    M_ARADDR;

    // Read data channel  
    logic                   S_RVALID,  M_RREADY;
    logic  [DATA_WIDTH-1:0] S_RDATA;
    logic  [1:0]            S_RRESP;

    // Write address channel
    logic                   M_AWVALID, S_AWREADY;
    logic  [ADDRESS-1:0]    M_AWADDR;

    // Write data channel
    logic                   M_WVALID,  S_WREADY;
    logic  [DATA_WIDTH-1:0] M_WDATA;
    logic  [3:0]            M_WSTRB;

    // Write response channel
    logic                   S_BVALID,  M_BREADY;
    logic  [1:0]            S_BRESP;

    // Expose to testbench — name makes clear who drives each signal
    assign R_data = S_RDATA;
    assign RVALID = S_RVALID;   // slave drives
    assign RREADY = M_RREADY;   // master drives
    assign RRESP  = S_RRESP;    // slave drives
    assign BVALID = S_BVALID;   // slave drives
    assign BREADY = M_BREADY;   // master drives
    assign BRESP  = S_BRESP;    // slave drives

    axi4_lite_master u_axi4_lite_master0 (
        .ACLK        (ACLK),
        .ARESETN     (ARESETN),
        .START_READ  (read_s),
        .START_WRITE (write_s),
        .address     (address),
        .W_data      (W_data),

        // Read address channel
        .M_ARVALID   (M_ARVALID),
        .M_ARADDR    (M_ARADDR),
        .M_ARREADY   (S_ARREADY),

        // Read data channel
        .M_RVALID    (S_RVALID),
        .M_RDATA     (S_RDATA),
        .M_RRESP     (S_RRESP),
        .M_RREADY    (M_RREADY),

        // Write address channel
        .M_AWVALID   (M_AWVALID),
        .M_AWADDR    (M_AWADDR),
        .M_AWREADY   (S_AWREADY),

        // Write data channel
        .M_WVALID    (M_WVALID),
        .M_WDATA     (M_WDATA),
        .M_WSTRB     (M_WSTRB),
        .M_WREADY    (S_WREADY),

        // Write response channel
        .M_BVALID    (S_BVALID),
        .M_BRESP     (S_BRESP),
        .M_BREADY    (M_BREADY)
    );

    axi4_lite_slave u_axi4_lite_slave0 (
        .ACLK        (ACLK),
        .ARESETN     (ARESETN),

        // Read address channel
        .S_ARVALID   (M_ARVALID),
        .S_ARADDR    (M_ARADDR),
        .S_ARREADY   (S_ARREADY),

        // Read data channel
        .S_RVALID    (S_RVALID),
        .S_RDATA     (S_RDATA),
        .S_RRESP     (S_RRESP),
        .S_RREADY    (M_RREADY),

        // Write address channel
        .S_AWVALID   (M_AWVALID),
        .S_AWADDR    (M_AWADDR),
        .S_AWREADY   (S_AWREADY),

        // Write data channel
        .S_WVALID    (M_WVALID),
        .S_WDATA     (M_WDATA),
        .S_WSTRB     (M_WSTRB),
        .S_WREADY    (S_WREADY),

        // Write response channel
        .S_BVALID    (S_BVALID),
        .S_BRESP     (S_BRESP),
        .S_BREADY    (M_BREADY)
    );

endmodule