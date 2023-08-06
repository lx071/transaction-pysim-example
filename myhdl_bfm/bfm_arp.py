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
def arp(clk, rst, s_eth_hdr_valid, s_eth_hdr_ready, s_eth_dest_mac, s_eth_src_mac, s_eth_type, 
        s_eth_payload_axis_tdata, s_eth_payload_axis_tkeep, s_eth_payload_axis_tvalid, s_eth_payload_axis_tready, s_eth_payload_axis_tlast, s_eth_payload_axis_tuser, 
        m_eth_hdr_valid, m_eth_hdr_ready, m_eth_dest_mac, m_eth_src_mac, m_eth_type, 
        m_eth_payload_axis_tdata, m_eth_payload_axis_tkeep, m_eth_payload_axis_tvalid, m_eth_payload_axis_tready, m_eth_payload_axis_tlast, m_eth_payload_axis_tuser, 
        arp_request_valid, arp_request_ready, arp_request_ip, arp_response_valid, arp_response_ready, arp_response_error, arp_response_mac, 
        local_mac, local_ip, gateway_ip, subnet_mask, clear_cache):
    @instance
    def logic():
        yield
    return logic


@block
def bfm():
    
    ### 参数定义

    DATA_WIDTH = 8
    KEEP_WIDTH = (DATA_WIDTH/8)

    TOTAL_WIDTH = 336
    TX_NUM = 28


    ### 信号定义

    # /*
    #     * Ethernet frame input
    #     */
    s_eth_hdr_valid = Signal(bool(0))
    s_eth_hdr_ready = Signal(bool(0))
    s_eth_dest_mac = Signal(modbv(0)[48:])
    s_eth_src_mac = Signal(modbv(0)[48:])
    s_eth_type = Signal(modbv(0)[16:])
    s_eth_payload_axis_tdata = Signal(modbv(0)[DATA_WIDTH:])
    s_eth_payload_axis_tkeep = Signal(modbv(0)[KEEP_WIDTH:])
    s_eth_payload_axis_tvalid = Signal(bool(0))
    s_eth_payload_axis_tready = Signal(bool(0))
    s_eth_payload_axis_tlast = Signal(bool(0))
    s_eth_payload_axis_tuser = Signal(bool(0))


    # /*
    #     * Ethernet frame output
    #     */
    m_eth_hdr_valid = Signal(bool(0))
    m_eth_hdr_ready = Signal(bool(0))
    m_eth_dest_mac = Signal(modbv(0)[48:])
    m_eth_src_mac = Signal(modbv(0)[48:])
    m_eth_type = Signal(modbv(0)[16:])
    m_eth_payload_axis_tdata = Signal(modbv(0)[DATA_WIDTH:])
    m_eth_payload_axis_tkeep = Signal(modbv(0)[KEEP_WIDTH:])
    m_eth_payload_axis_tvalid = Signal(bool(0))
    m_eth_payload_axis_tready = Signal(bool(0))
    m_eth_payload_axis_tlast = Signal(bool(0))
    m_eth_payload_axis_tuser = Signal(bool(0))


    # /*
    #     * ARP requests
    #     */
    arp_request_valid = Signal(bool(0))
    arp_request_ready = Signal(bool(0))
    arp_request_ip = Signal(modbv(0)[32:])
    arp_response_valid = Signal(bool(0))
    arp_response_ready = Signal(bool(0))
    arp_response_error = Signal(bool(0))
    arp_response_mac = Signal(modbv(0)[48:])


    # /*
    #     * Configuration
    #     */
    local_mac = Signal(modbv(0)[48:])
    local_ip = Signal(modbv(0)[32:])
    gateway_ip = Signal(modbv(0)[32:])
    subnet_mask = Signal(modbv(0)[32:])
    clear_cache = Signal(bool(0))


    tx_payload_data = Signal(modbv(0)[TOTAL_WIDTH:])
    tx_arp_payload_data = Signal(modbv(0)[TOTAL_WIDTH-112:])
    rx_arp_payload_data = Signal(modbv(0)[TOTAL_WIDTH-112:])


    clk = Signal(bool(0))
    rst = ResetSignal(0, active=0, isasync=True)

    tx_en = Signal(bool(0))
    rx_en = Signal(bool(0))
    
    tck = Signal(bool(0))
    rck = Signal(bool(0))

    tx_state = Signal(bool(0))
    tx_num = Signal(intbv(0, min=0, max=TX_NUM+1))
    xmit_state = enum('INIT', 'RUN')

    rx_state = Signal(bool(0))
    recv_state = enum('INIT', 'RUN')


    unused_signal = [rst, s_eth_hdr_ready, s_eth_payload_axis_tready, 
        m_eth_hdr_valid, m_eth_dest_mac, m_eth_src_mac, m_eth_type, m_eth_payload_axis_tdata, m_eth_payload_axis_tkeep, m_eth_payload_axis_tvalid, m_eth_payload_axis_tlast, m_eth_payload_axis_tuser, 
        arp_request_ready, arp_response_valid, arp_response_error, arp_response_mac]
    
    for signal in unused_signal:
        signal._driven = 'reg'
        signal._used = True
    
    tx_payload_data._driven = 'reg'

    
    ### 时钟激励
    clkdriver = ClkDriver(clk=clk, period=8)  # named association

    @always(clk.posedge, clk.negedge)
    def tx_clkdriver():
        if tx_en:
            tck.next = clk
        else:
            tck.next = 0
    
    @always(clk.posedge, clk.negedge)
    def rx_clkdriver():
        if rx_en:
            rck.next = clk
        else:
            rck.next = 0

    ### 复位设置

    @instance
    def stimulus():

        subnet_mask.next = 0
    
        s_eth_payload_axis_tuser.next = 0

        m_eth_hdr_ready.next = 1
        m_eth_payload_axis_tready.next = 1

        arp_request_valid.next = 0
        arp_request_ip.next = 0
        arp_response_ready.next = 0

        local_mac.next = 0
        local_ip.next = 0
        gateway_ip.next = 0
        subnet_mask.next = 0
        clear_cache.next = 0

        yield clk.posedge


    ### 逻辑处理

    @always(tck.posedge, rst.posedge)
    def arp_tx():
        if rst:
            tx_en.next = 0
            s_eth_hdr_valid.next = 0
            s_eth_dest_mac.next = 0
            s_eth_src_mac.next = 0
            s_eth_type.next = 0
            tx_arp_payload_data.next = 0

            s_eth_payload_axis_tkeep.next = 0
            s_eth_payload_axis_tvalid.next = 0
            s_eth_payload_axis_tdata.next = 0
            s_eth_payload_axis_tlast.next = 0

            tx_num.next = 0
            tx_state.next = xmit_state.INIT
        else:
            if tx_state == xmit_state.INIT:
                s_eth_hdr_valid.next = 1
                s_eth_dest_mac.next = tx_payload_data[TOTAL_WIDTH:TOTAL_WIDTH-48]
                s_eth_src_mac.next = tx_payload_data[TOTAL_WIDTH-48:TOTAL_WIDTH-96]
                s_eth_type.next = tx_payload_data[TOTAL_WIDTH-96:TOTAL_WIDTH-112]
                tx_arp_payload_data.next = tx_payload_data[TOTAL_WIDTH-112:0]

                s_eth_payload_axis_tkeep.next = 1
                s_eth_payload_axis_tvalid.next = 1
                s_eth_payload_axis_tdata.next = 0

                tx_state.next = xmit_state.RUN
            elif tx_state == xmit_state.RUN:

                if tx_num == 0:
                    s_eth_hdr_valid.next = 0
                
                
                if tx_num <= TX_NUM - 1:
                    s_eth_payload_axis_tdata.next = tx_arp_payload_data[TOTAL_WIDTH-112:TOTAL_WIDTH-113-7]
                    tx_arp_payload_data.next = (tx_arp_payload_data << 8)
                    tx_num.next = tx_num + 1
                

                if tx_num == TX_NUM -1:
                    s_eth_payload_axis_tlast.next = 1
                    tx_num.next = tx_num + 1
                    
                if tx_num == TX_NUM:
                    s_eth_payload_axis_tlast.next = 0
                    s_eth_payload_axis_tvalid.next = 0
                    tx_num.next = 0
                    tx_state.next = xmit_state.INIT
                    tx_en.next = 0

            else:
                raise ValueError("Undefined state")

    
    @always(rck.posedge, rst.posedge)
    def arp_rx():
        if rst:
            rx_en.next = 0
            rx_arp_payload_data.next = 0
            rx_state.next = recv_state.INIT
        else:
            if rx_state == recv_state.INIT:
                if m_eth_hdr_valid == 1:
                    rx_state.next = recv_state.RUN

            elif rx_state == recv_state.RUN:
                
                if(m_eth_payload_axis_tvalid == 1):
                    rx_arp_payload_data.next = (rx_arp_payload_data << DATA_WIDTH) + m_eth_payload_axis_tdata

                if(m_eth_payload_axis_tlast == 1):
                    rx_state.next = recv_state.INIT
                    rx_en.next = 0
                
            else:
                raise ValueError("Undefined state")     


    ### DUT
    
    return clkdriver, tx_clkdriver, rx_clkdriver, stimulus, arp_tx, arp_rx


def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    arp_bfm = bfm()

    arp_bfm.convert(hdl=hdl, testbench=False, timescale='1ns/1ps')

    clk, rst, s_eth_hdr_valid, s_eth_hdr_ready, s_eth_dest_mac, s_eth_src_mac, s_eth_type, \
        s_eth_payload_axis_tdata, s_eth_payload_axis_tkeep, s_eth_payload_axis_tvalid, s_eth_payload_axis_tready, s_eth_payload_axis_tlast, s_eth_payload_axis_tuser, \
        m_eth_hdr_valid, m_eth_hdr_ready, m_eth_dest_mac, m_eth_src_mac, m_eth_type, \
        m_eth_payload_axis_tdata, m_eth_payload_axis_tkeep, m_eth_payload_axis_tvalid, m_eth_payload_axis_tready, m_eth_payload_axis_tlast, m_eth_payload_axis_tuser, \
        arp_request_valid, arp_request_ready, arp_request_ip, arp_response_valid, arp_response_ready, arp_response_error, arp_response_mac, \
        local_mac, local_ip, gateway_ip, subnet_mask, clear_cache = [Signal() for i in range(36)]
    inst_arp = arp(clk, rst, s_eth_hdr_valid, s_eth_hdr_ready, s_eth_dest_mac, s_eth_src_mac, s_eth_type, \
        s_eth_payload_axis_tdata, s_eth_payload_axis_tkeep, s_eth_payload_axis_tvalid, s_eth_payload_axis_tready, s_eth_payload_axis_tlast, s_eth_payload_axis_tuser, \
        m_eth_hdr_valid, m_eth_hdr_ready, m_eth_dest_mac, m_eth_src_mac, m_eth_type, \
        m_eth_payload_axis_tdata, m_eth_payload_axis_tkeep, m_eth_payload_axis_tvalid, m_eth_payload_axis_tready, m_eth_payload_axis_tlast, m_eth_payload_axis_tuser, \
        arp_request_valid, arp_request_ready, arp_request_ip, arp_response_valid, arp_response_ready, arp_response_error, arp_response_mac, \
        local_mac, local_ip, gateway_ip, subnet_mask, clear_cache)

    tbpath = 'inst.v'
    tbfile = open(tbpath, 'w')
    writeInst(tbfile, inst_arp)
    tbfile.close()

    bfm_name = arp_bfm.func.__name__
    
    filename1 = bfm_name + '.v'
    filename2 = tbpath
    filename3 = bfm_name + '_arp.v'
    merge(filename1, filename2, filename3)


if __name__ == '__main__':
    convert_inc(hdl='Verilog')
    
    