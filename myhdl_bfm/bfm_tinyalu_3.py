from myhdl import *
from utils import writeInst, merge

@block
def ClkDriver(clk, period=20):

    lowTime = int(period / 2)
    highTime = period - lowTime

    @instance
    def drive_clk():
        while True:
            yield delay(lowTime)
            clk.next = 1
            yield delay(highTime)
            clk.next = 0

    return drive_clk


@block
def tinyalu(clk, A_s, B_s, op_s, reset_n, start, done, res_o):
    @instance
    def logic():
        yield
    return logic
    

@block
def bfm(data, xmit_en, res_o):
    """ bfm

    res_o -- output
    """
    
    ### 参数定义

    DATA_WIDTH = 8
    PACKAGE_WIDTH = 2400
    
    RESET_DELAY = 10
    NUM = 100

    ### 信号定义

    num = Signal(intbv(0, min=0, max=NUM+1))

    clk = Signal(bool(0))
    # reset_i = Signal(bool(0))
    reset_n = ResetSignal(0, active=0, isasync=True)

    A_s = Signal(modbv(0)[DATA_WIDTH:])
    B_s = Signal(modbv(0)[DATA_WIDTH:])
    op_s = Signal(modbv(0)[3:])

    start = Signal(bool(0))
    done = Signal(bool(0))
    payload_data = Signal(modbv(0)[PACKAGE_WIDTH:])

    flag = Signal(bool(0))
    
    
    ### 时钟激励
    clkdriver = ClkDriver(clk=clk, period=10)  # named association


    ### 复位设置

    @instance
    def stimulus():

        reset_n.next = 0

        for i in range(RESET_DELAY):
            yield clk.posedge
        
        reset_n.next = 1
        # raise StopSimulation

    ### 逻辑处理

    # @always_seq(clk_i.posedge, reset=reset_i)
    @always(clk.posedge)
    def add():
        if not reset_n:
            A_s.next = 0
            B_s.next = 0
            op_s.next = 0
            start.next = 0
            num.next = 0   
        else:
            if xmit_en:
                if not flag:
                    payload_data.next = data
                    flag.next = 1
                if flag:
                    op_s.next = payload_data[3:0]
                    A_s.next = payload_data[16:8]
                    B_s.next = payload_data[24:16]
                    start.next = 1
                    payload_data.next = (payload_data >> 24)
                    num.next = num + 1

            if num >= NUM-1:
                num.next = 0
                xmit_en.next = 0
                flag.next = 0         

    ### DUT

    return clkdriver, stimulus, add


def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    m = 16

    PACKAGE_WIDTH = 2400
    
    data = Signal(modbv(0)[PACKAGE_WIDTH:])
    xmit_en = Signal(bool(0))
    res = Signal(modbv(0)[m:])
    res._driven = 'reg'

    tinyalu_bfm = bfm(data, xmit_en, res)

    tinyalu_bfm.convert(hdl=hdl, testbench=False, timescale='1ns/1ps')

    clk, A_s, B_s, op_s, reset_n, start, done, res_o = [Signal() for i in range(8)]
    inst_tinyalu = tinyalu(clk, A_s, B_s, op_s, reset_n, start, done, res_o)

    tbpath = 'inst.v'
    tbfile = open(tbpath, 'w')
    writeInst(tbfile, inst_tinyalu)
    tbfile.close()

    bfm_name = tinyalu_bfm.func.__name__
    
    filename1 = bfm_name + '.v'
    filename2 = tbpath
    filename3 = bfm_name + '_tinyalu_3.v'
    merge(filename1, filename2, filename3)


if __name__ == '__main__':
    convert_inc(hdl='Verilog')
    
    