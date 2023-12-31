// File: bfm.v
// Generated by MyHDL 0.11
// Date: Tue Aug  8 05:51:00 2023


`timescale 1ns/1ps

module bfm (
    data,
    xmit_en,
    res_o
);
// bfm
// 
// res_o -- output

input [1599:0] data;
output xmit_en;
reg xmit_en;
output [7:0] res_o;
reg [7:0] res_o;

reg [7:0] A_s;
reg [7:0] B_s;
reg clk;
reg flag;
reg [6:0] num;
reg [1599:0] payload_data;
reg reset;



initial begin: BFM_CLKDRIVER0_DRIVE_CLK
    while (1'b1) begin
        # 5;
        clk <= 1;
        # 5;
        clk <= 0;
    end
end


initial begin: BFM_STIMULUS
    reset <= 0;
    @(posedge clk);
end


always @(posedge clk) begin: BFM_ADD
    if (reset) begin
        A_s <= 0;
        B_s <= 0;
        num <= 0;
        flag <= 0;
    end
    else begin
        if (xmit_en) begin
            if ((!flag)) begin
                payload_data <= data;
                flag <= 1;
            end
            if (flag) begin
                A_s <= payload_data[8-1:0];
                B_s <= payload_data[16-1:8];
                payload_data <= (payload_data >>> 16);
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


Add dut(
    A_s,
    B_s,
    res_o,
    clk,
    reset
);

endmodule
