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
def PoseidonTopLevel(io_input_valid, io_input_ready, io_input_last, io_input_payload, 
                        io_output_valid, io_output_ready, io_output_last, io_output_payload,
                            clk, resetn):
    @instance
    def logic():
        yield
    return logic
    

@block
def bfm():
    
    ### 参数定义

    DATA_WIDTH = 255
    PACKAGE_WIDTH = 7650
    NUM = 30

    ### 信号定义
    
    io_input_valid = Signal(bool(0))
    io_output_ready = Signal(bool(0))
    io_input_last = Signal(bool(0))
    io_input_payload = Signal(modbv(0)[DATA_WIDTH:])

    io_output_valid = Signal(bool(0))
    io_input_ready = Signal(bool(0))
    io_output_last = Signal(bool(0))
    io_output_payload = Signal(modbv(0)[DATA_WIDTH:])

    clk = Signal(bool(0))
    resetn = ResetSignal(0, active=0, isasync=True)

    xmit_en = Signal(bool(0))
    i = Signal(intbv(0, min=0, max=4))
    num = Signal(intbv(0, min=0, max=NUM+1))
    
    data = Signal(modbv(0)[PACKAGE_WIDTH:])

    
    resetn._driven = 'reg'
    io_output_valid._driven = 'wire'
    io_input_ready._driven = 'wire'
    io_output_last._driven = 'wire'
    io_output_payload._driven = 'wire'
    io_output_ready._driven = 'reg'
    
    io_output_valid._used = True
    io_input_ready._used = True
    io_output_last._used = True
    io_output_payload._used = True
    io_output_ready._used = True

    
    ### 时钟激励

    clkdriver = ClkDriver(clk=clk, period=10)  # named association


    ### 逻辑处理

    # @always_seq(clk_i.posedge, reset=reset_i)
    @always(clk.posedge)
    def hash():
        if not resetn:
            xmit_en.next = 0
            i.next = 0
            num.next = 0
            io_input_valid.next = 0
            io_input_last.next = 0
            io_input_payload.next = 0
        else:
            
            if xmit_en:
                io_input_valid.next = 1
                num.next = num + 1
                io_input_payload.next = data[255:0]
                
                i.next = i + 1
                if i == 2: 
                    io_input_last.next = 1
                    i.next = 0
                else:
                    io_input_last.next = 0
                
                data.next = data >> 255

            if num >= NUM-1:
                num.next = 0
                xmit_en.next = 0

            if not xmit_en:
                io_input_valid.next = 0
            

    ### DUT
    
    return clkdriver, hash


def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    hash_bfm = bfm()

    hash_bfm.convert(hdl=hdl, testbench=False, timescale='1ns/1ps')

    io_input_valid, io_input_ready, io_input_last, io_input_payload, \
                        io_output_valid, io_output_ready, io_output_last, io_output_payload,\
                            clk, resetn = [Signal() for i in range(10)]
    inst_hash = PoseidonTopLevel(io_input_valid, io_input_ready, io_input_last, io_input_payload, 
                                        io_output_valid, io_output_ready, io_output_last, io_output_payload,
                                            clk, resetn)

    tbpath = 'inst.v'
    tbfile = open(tbpath, 'w')
    writeInst(tbfile, inst_hash)
    tbfile.close()

    bfm_name = hash_bfm.func.__name__
    
    filename1 = bfm_name + '.v'
    filename2 = tbpath
    filename3 = bfm_name + '_hash.v'
    merge(filename1, filename2, filename3)


if __name__ == '__main__':
    convert_inc(hdl='Verilog')
    
    