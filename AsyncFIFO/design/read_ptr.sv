`ifndef READ_PTR_SV
`define READ_PTR_SV

module read_ptr #(parameter ptr_width=9)( rclk, r_rst_n, r_en,   wptr_sync,  raddr, rptr,  empty);

input bit rclk,r_rst_n, r_en;
input logic [ptr_width-1:0]  wptr_sync;
output bit empty;
output logic [ptr_width-1:0] raddr, rptr;

 logic rempty;

logic [ptr_width-1:0]raddr_next;
logic [ptr_width-1:0]rptr_next;


assign raddr_next= raddr + (r_en & !empty); //increment only if empty
assign rptr_next=(raddr_next>>1)^raddr_next; // GRAY CONVERTED VALUE
assign rempty= (wptr_sync == rptr_next); // CHECKING THE EMPTY CONDITION 

always_ff@(posedge rclk or negedge r_rst_n)
begin
	if(!r_rst_n)
		begin
		raddr<=0; //default value
		rptr<=0;
		end 
	else begin
		raddr<=raddr_next;//incrementing binary read pointer
		rptr<=rptr_next;//incrementing gray read pointer
	end
end

always_ff@(posedge rclk or negedge r_rst_n)
begin
if(!r_rst_n)
	empty<=1;//initial empty condition
else
	empty<=rempty;
	
end

endmodule
`endif