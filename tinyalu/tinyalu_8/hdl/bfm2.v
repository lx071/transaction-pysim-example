`timescale 1ns/1ps

module bfm
(
input reg [PACKAGE_WIDTH-1:0] data,
output reg xmit_en,
output  wire [15:0] res_o
);

parameter NUM=100;
parameter PACKAGE_WIDTH=2400;
parameter RESET_DELAY=10;

reg clk, reset_n;
reg start, done;

reg [7:0] A_s;
reg [7:0] B_s;
reg [2:0] op_s;

int num = 0;
reg [PACKAGE_WIDTH-1:0] payload_data;

always #5 clk = ~clk;


initial begin
    //clk = 0;
    reset_n <= 0;
    A_s <= 0;
    B_s <= 0;
    op_s <= 0;
    start <= 0;
    payload_data <= 0;
    repeat(RESET_DELAY) @(posedge clk);
    reset_n <= 1;
end

tinyalu inst_tinyalu(
    .clk(clk),
    .A(A_s),
    .B(B_s),
    .op(op_s),
    .reset_n(reset_n),
    .start(start),
    .done(done),
    .result(res_o)
);

reg flag;
always @(posedge clk) begin
    if(!reset_n) begin
        A_s <= 8'h0;
        B_s <= 8'h0;
        op_s <= 3'h0;
        start <= 0;
        flag <= 0;
    end else begin   
        if(xmit_en) begin
            if(!flag) begin
                payload_data <= data;
                flag <= 1;
            end
            if(flag) begin
                op_s <= payload_data[2:0];
                A_s <= payload_data[15:8];
                B_s <= payload_data[23:16];
                start <= 1;
                payload_data <= (payload_data >> 24);
                num <= num + 1;

                $display("res_o:", res_o);
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