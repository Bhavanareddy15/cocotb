module fifo_debug #(
  parameter int DEPTH = 4,
  parameter int WIDTH = 8
) (
  input  logic             clk,
  input  logic             rst,
  input  logic             wr_en,
  input  logic             rd_en,
  input  logic [WIDTH-1:0] din,
  output logic [WIDTH-1:0] dout,
  output logic             full,
  output logic             empty
);
  logic [WIDTH-1:0]        mem   [0:DEPTH-1];
  logic [$clog2(DEPTH)-1:0] wptr, rptr;
  logic [$clog2(DEPTH+1)-1:0] count;

  // FIX: correct thresholds
  assign full  = (count == DEPTH);
  assign empty = (count == 0);

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      wptr  <= '0;
      rptr  <= '0;
      count <= '0;
      dout  <= '0;
    end else begin
      // FIX: single count update handles all cases correctly
      unique case ({wr_en && !full, rd_en && !empty})
        2'b10: count <= count + 1'b1;
        2'b01: count <= count - 1'b1;
        default: count <= count;   // both or neither — net zero
      endcase

      if (wr_en && !full) begin
        mem[wptr] <= din;
        wptr      <= (wptr == DEPTH-1) ? '0 : wptr + 1'b1;
      end

      if (rd_en && !empty) begin
        dout <= mem[rptr];
        rptr <= (rptr == DEPTH-1) ? '0 : rptr + 1'b1;
      end
    end
  end
endmodule