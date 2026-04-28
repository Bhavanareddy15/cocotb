`ifndef READ_PTR_SV
`define READ_PTR_SV

module read_ptr #(parameter ptr_width=8)( rclk, r_rst_n, r_en,   wptr_sync,  raddr, rptr,  empty);

input bit rclk,r_rst_n, r_en;
input logic [ptr_width:0]  wptr_sync;
output bit empty;
output logic [ptr_width:0] raddr, rptr;

 logic rempty;
 logic emptyr;
 logic readempty;

logic [ptr_width:0]raddr_next;
logic [ptr_width:0]rptr_next;


assign raddr_next= raddr + (r_en & !empty);
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
//Assertions
property P_rreset;
	@(posedge rclk)
	disable iff(r_rst_n)
	!r_rst_n |=> (raddr=='0 & rptr=='0);
endproperty
a_rreset: assert property(P_rreset)
else
	$error(" assertion failed in read reset");
	
property P_rempty;
	@(posedge rclk)
	disable iff(r_rst_n)
	!r_rst_n |=> (empty=='1);
endproperty
a_empty: assert property(P_rempty)
else
	$error(" assertion failed in empty condition");

endmodule
`endif