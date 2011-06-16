#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from SPISlave import SPISlave
from NCO import NCO
from SwitchCtl import SwitchCtl

def HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp):
    """Harmonic digital interface
    
    clk     - input clock
    reset   - async reset to default values
    scl     - SPI clock
    cs      - SPI chip select
    din     - SPI MOSI
    dout    - SPI MISO

    swXx     - multiplier switches
    cintXx   - Cap on
    zeroXx   - Reset cap to Vcm
    fastXx   - gm x10
    tuneXx   - 12bit IDAC word
    """

    N = 16
    N_DATA_BITS = 16 + 2*N

    # SPI
    cdata = Signal(intbv(0)[N_DATA_BITS:])
    spiSlave = SPISlave(N_DATA_BITS, reset_in, scl_in, cs_in, din, dout, cdata)

    # pull out slices of SPI words
    cal = cdata(47)
    rst = cdata(46)
    seA = cdata(29)
    seB = cdata(13)
    fcw = cdata(46,32)

    # NCO
    mA = Signal(intbv(0)[0])
    mB = Signal(intbv(0)[0])
    nco = NCO(N, clk_in, reset_in, rst, fcw, nco_i, nco_q)

    # Channels
    sA = Signal(intbv(0)[7:])
    sB = Signal(intbv(0)[7:])
    channelA = SwitchCtl(multA, cal, seA, sA)
    channelB = SwitchCtl(multB, cal, seB, sB)

    @always(clk_in.posedge)
    def switchOut():
        swAn.next = sA
        swAp.next = ~sA
        swBn.next = sB
        swBp.next = ~sB

    @always(cdata)
    def passthru():
        cintAn.next = cdata[31]
        cintAp.next = not cdata[31]

        zeroAn.next = cdata[30]
        zeroAp.next = not cdata[30]

        fastAn.next = cdata[28]
        fastAp.next = not cdata[28]

        tuneAn.next = cdata[28:16]
        tuneAp.next = ~intbv(cdata[28:16], max=2**12)

        cintBn.next = cdata[15]
        cintBp.next = not cdata[15]

        zeroBn.next = cdata[14]
        zeroBp.next = not cdata[14]

        fastBn.next = cdata[12]
        fastBp.next = not cdata[12]

        tuneBn.next = cdata[12:0]
        tuneBp.next = ~intbv(cdata[12:0], max=2**12)

    @always_comb
    def thrulines():
        clk_out.next = clk_in
        reset_out.next = reset_in
        scl_out.next = scl_in
        cs_out.next = cs_in

    return instances()


def convert():
    clk_in, reset_in, scl_in, cs_in = [Signal(intbv(0)[0]) for i in range(4)]
    clk_out, reset_out, scl_out, cs_out = [Signal(intbv(0)[0]) for i in range(4)]
    din, dout = [Signal(intbv(0)[0]) for i in range(2)]
    nco_i, nco_q = [Signal(intbv(0)[0]) for i in range(2)]
    multA, multB = [Signal(intbv(0)[0]) for i in range(2)]

    swAn = Signal(intbv(0)[7:])
    swAp = Signal(intbv(0)[7:])
    swBn = Signal(intbv(0)[7:])
    swBp = Signal(intbv(0)[7:])

    cintAn, zeroAn, fastAn = [Signal(intbv(0)[0]) for i in range(3)]
    cintAp, zeroAp, fastAp = [Signal(intbv(0)[0]) for i in range(3)]

    cintBn, zeroBn, fastBn = [Signal(intbv(0)[0]) for i in range(3)]
    cintBp, zeroBp, fastBp = [Signal(intbv(0)[0]) for i in range(3)]

    tuneAn = Signal(intbv(0)[12:])
    tuneAp = Signal(intbv(0)[12:])

    tuneBn = Signal(intbv(0)[12:])
    tuneBp = Signal(intbv(0)[12:])

    toVerilog(
        HarmonicInterface,
        clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp)

if __name__ == '__main__':
    convert()

