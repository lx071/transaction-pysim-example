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
def Add(A_s, B_s, res_o, clk, reset):
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

    NUM = 100
    DATA_WIDTH = 8
    PACKAGE_WIDTH = 1600


    ### 信号定义

    num = Signal(intbv(0, min=0, max=NUM+1))

    clk = Signal(bool(0))
    # reset = Signal(bool(0))
    reset = ResetSignal(0, active=0, isasync=True)

    A_s = Signal(modbv(0)[DATA_WIDTH:])
    B_s = Signal(modbv(0)[DATA_WIDTH:])
    payload_data = Signal(modbv(0)[PACKAGE_WIDTH:])

    flag = Signal(bool(0))
    
    ### 时钟激励
    clkdriver = ClkDriver(clk=clk, period=10)  # named association


    ### 复位设置

    @instance
    def stimulus():
        reset.next = 0
        yield clk.posedge
        # raise StopSimulation


    ### 逻辑处理

    # @always_seq(clk.posedge, reset=reset)
    @always(clk.posedge)
    def add():
        if reset:
            A_s.next = 0
            B_s.next = 0
            num.next = 0
            flag.next = 0
        else:
            if xmit_en:
                if not flag:
                    payload_data.next = data
                    flag.next = 1
                if flag:
                    A_s.next = payload_data[8:0]
                    B_s.next = payload_data[16:8]
                    payload_data.next = (payload_data >> 16)
                    num.next = num + 1

            if num >= NUM-1:
                num.next = 0
                xmit_en.next = 0
                flag.next = 0


    ### DUT

    return clkdriver, stimulus, add


def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    PACKAGE_WIDTH = 1600
    
    data = Signal(modbv(0)[PACKAGE_WIDTH:])
    xmit_en = Signal(bool(0))
    res = Signal(modbv(0)[8:])
    res._driven = 'reg'

    add_bfm = bfm(data, xmit_en, res)

    add_bfm.convert(hdl=hdl, testbench=False, timescale='1ns/1ps')

    A_s, B_s, res_o, clk, reset = [Signal() for i in range(5)]
    inst_add = Add(A_s, B_s, res_o, clk, reset)

    tbpath = 'inst.v'
    tbfile = open(tbpath, 'w')
    writeInst(tbfile, inst_add)
    tbfile.close()

    bfm_name = add_bfm.func.__name__
    
    filename1 = bfm_name + '.v'
    filename2 = tbpath
    filename3 = bfm_name + '_add_3.v'
    merge(filename1, filename2, filename3)


if __name__ == '__main__':
    convert_inc(hdl='Verilog')
    
    