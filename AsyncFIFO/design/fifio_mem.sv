`ifndef FIFO_MEM_SV
`define FIFO_MEM_SV

module fifo_mem #(parameter data_width =  8, ptr_width =  9, depth =409)( wclk,rclk,r_rst_n,w_rst_n,w_en,r_en,full,empty, data_in,  waddr,raddr,  data_out);

input bit wclk,rclk,r_rst_n,w_rst_n,w_en,r_en,full,empty;
input logic [ptr_width:0]  waddr, raddr;

input logic [data_width-1:0] data_in;
output logic [data_width-1:0]data_out;

logic [data_width-1:0] fifo [0: depth-1];

  always_ff@(posedge wclk)
begin
  if(w_en & !full & w_rst_n)
begin
fifo[waddr[ptr_width-1:0]]<=data_in; // WRITE OPERATION
end
end
assign data_out=fifo[raddr[ptr_width-1:0]]; // READ OPERATION
endmodule
`endif