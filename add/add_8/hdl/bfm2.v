`timescale 1ns/1ps

module bfm
(
input reg [PACKAGE_WIDTH-1:0] data,
output reg xmit_en,
output  wire [7:0] res_o
);

parameter NUM=100;
parameter PACKAGE_WIDTH=1600;


reg clk, reset;

reg [7:0] A_s;
reg [7:0] B_s;

int num = 0;
reg [PACKAGE_WIDTH-1:0] payload_data;

Add inst_add(
    .io_A(A_s),
    .io_B(B_s),
    .io_X(res_o),
    .clk(clk),
    .reset(reset)
);

always #5 clk = ~clk;

initial begin
    clk <= 0;
    reset <= 0;
    //xmit_en <= 0;
end

reg flag = 0;
always @(posedge clk) begin

    if(reset) begin
        A_s <= 8'h0;
        B_s <= 8'h0;
    end else begin   
        if(xmit_en) begin
            if(!flag) begin
                payload_data <= data;
                flag <= 1;
            end
            if(flag) begin
                A_s <= payload_data[7:0];
                B_s <= payload_data[15:8];
                payload_data <= (payload_data >> 16);
                num <= num + 1;
                //$display("A_s:", A_s);
            end
        end    
        if(num >= NUM-1) begin
            num <= 0;
            xmit_en <= 0;
            flag <= 0;
        end 
    end
end

initial begin
    //$dumpfile("dump.vcd");
    //$dumpvars;
end

endmodule