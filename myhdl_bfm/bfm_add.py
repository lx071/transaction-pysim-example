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
def MyTopLevel(A_s, B_s, res_o, clk_i, reset_i):
    @instance
    def logic():
        yield
    return logic
    

@block
def bfm(res_o):
    """ bfm

    res_o -- output
    """
    
    ### 参数定义

    DATA_WIDTH = 8
    PACKAGE_WIDTH = 1600
    
    RESET_DELAY = 10
    NUM = 100

    ### 信号定义

    num = Signal(intbv(0, min=0, max=NUM+1))

    clk_i = Signal(bool(0))
    # reset_i = Signal(bool(0))
    reset_i = ResetSignal(0, active=0, isasync=True)

    xmit_en = Signal(bool(0))
    
    A_s = Signal(modbv(0)[DATA_WIDTH:])
    B_s = Signal(modbv(0)[DATA_WIDTH:])

    data = Signal(modbv(0)[PACKAGE_WIDTH:])

    
    ### 时钟激励

    clkdriver = ClkDriver(clk=clk_i, period=10)  # named association

    ### 复位设置

    @instance
    def stimulus():
        reset_i.next = 1

        for i in range(RESET_DELAY):
            yield clk_i.posedge
        
        reset_i.next = 0
        # raise StopSimulation

    ### 逻辑处理

    # @always_seq(clk_i.posedge, reset=reset_i)
    @always(clk_i.posedge)
    def add():
        if reset_i:
            A_s.next = 0
            B_s.next = 0
            num.next = 0
        else:
            if xmit_en:
                A_s.next = data[8:0]
                B_s.next = data[16:8]
                data.next = (data >> 16)
                num.next = num + 1

            if num >= NUM:
                num.next = 0
                xmit_en.next = 0


    ### DUT

    return clkdriver, stimulus, add


def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    m = 8

    res = Signal(modbv(0)[m:])
    res._driven = 'reg'

    add_bfm = bfm(res)

    add_bfm.convert(hdl=hdl, testbench=False, timescale='1ns/1ps')

    A_s, B_s, res_o, clk_i, reset_i = [Signal() for i in range(5)]
    inst_add = MyTopLevel(A_s, B_s, res_o, clk_i, reset_i)

    tbpath = 'inst.v'
    tbfile = open(tbpath, 'w')
    writeInst(tbfile, inst_add)
    tbfile.close()

    bfm_name = add_bfm.func.__name__
    
    filename1 = bfm_name + '.v'
    filename2 = tbpath
    filename3 = bfm_name + '_add.v'
    merge(filename1, filename2, filename3)


if __name__ == '__main__':
    convert_inc(hdl='Verilog')
    
    