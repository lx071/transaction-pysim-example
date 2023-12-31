// File: bfm.v
// Generated by MyHDL 0.11
// Date: Tue Aug  8 06:33:04 2023


`timescale 1ns/1ps

module bfm (
    data,
    xmit_en,
    res_o
);
// bfm
// 
// res_o -- output

input [2399:0] data;
output xmit_en;
reg xmit_en;
output [15:0] res_o;
reg [15:0] res_o;

reg [7:0] A_s;
reg [7:0] B_s;
reg clk;
reg flag;
reg [6:0] num;
reg [2:0] op_s;
reg [2399:0] payload_data;
reg reset_n;
reg start;



initial begin: BFM_CLKDRIVER0_DRIVE_CLK
    while (1'b1) begin
        # 5;
        clk <= 1;
        # 5;
        clk <= 0;
    end
end


initial begin: BFM_STIMULUS
    integer i;
    reset_n <= 0;
    for (i=0; i<10; i=i+1) begin
        @(posedge clk);
    end
    reset_n <= 1;
end


always @(posedge clk) begin: BFM_ADD
    if ((!reset_n)) begin
        A_s <= 0;
        B_s <= 0;
        op_s <= 0;
        start <= 0;
        num <= 0;
    end
    else begin
        if (xmit_en) begin
            if ((!flag)) begin
                payload_data <= data;
                flag <= 1;
            end
            if (flag) begin
                op_s <= payload_data[3-1:0];
                A_s <= payload_data[16-1:8];
                B_s <= payload_data[24-1:16];
                start <= 1;
                payload_data <= (payload_data >>> 24);
                num <= (num + 1);
            end
        end
        if (($signed({1'b0, num}) >= (100 - 1))) begin
            num <= 0;
            xmit_en <= 0;
            flag <= 0;
        end
    end
end


tinyalu dut(
    clk,
    A_s,
    B_s,
    op_s,
    reset_n,
    start,
    done,
    res_o
);

endmodule
