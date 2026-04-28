`ifndef WRITE_PTR_SV
`define WRITE_PTR_SV

module write_ptr #(parameter ptr_width=9)(wclk, w_rst_n, w_en,  rptr_sync,  waddr, wptr, full);

input bit wclk, w_rst_n, w_en;
input logic [ptr_width:0] rptr_sync;

output bit full;
output logic [ptr_width:0] waddr, wptr;

logic wfull;
logic [ptr_width:0]waddr_next; 
logic [ptr_width:0]wptr_next;

assign waddr_next= waddr + (w_en & !full);
assign wptr_next= (waddr_next>>1)^waddr_next; 

always_ff@(posedge wclk or negedge w_rst_n)
begin
	if(!w_rst_n)
		begin
		waddr<='0; //set default value
		wptr<='0;
		end 
	else begin
		waddr<=waddr_next;//incrementing binary write pointer
		wptr<=wptr_next;//incrementing gray write pointer
	end
end

always_ff@(posedge wclk or negedge w_rst_n)
begin
if(!w_rst_n)
	full<=0;
else
	full<=wfull;
end
assign wfull= (wptr_next=={~rptr_sync[ptr_width:ptr_width-1],rptr_sync[ptr_width-2:0]});// FULL CONDITION

//assertions
property P_wreset;
	@(posedge wclk)
	disable iff(w_rst_n)
	!w_rst_n |=> ((waddr=='0) & (wptr=='0));
endproperty
a_reset: assert property(P_wreset)
else
	$error(" assertion failed in write reset");
	
property P_wfull;
	@(posedge wclk)
	disable iff(w_rst_n)
	!w_rst_n |=> full=='0;
endproperty
a_full: assert property(P_wfull)
else
	$error(" assertion failed in write full condition");
	
endmodule
  `endif