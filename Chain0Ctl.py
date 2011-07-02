#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from SPISlave import SPISlave
from AnalogMuxCtl import AnalogMuxCtl
from BufferCtl import BufferCtl

def Chain0Ctl(reset, scl, cs, din,
        lfxtal, timer0,
        dout,
        sw0n, sw0p,
        tune0n, tune0p):
    """Harmonic chain 0 multiplexer, NCO clock, and pad buffer control

    Inputs:
    reset   - reset SPI register
    scl     - SPI SCLK
    cs      - SPI CS
    din     - SPI MOSI
    lfxtal  - 32k crystal
    timer0  - NS430 timer0 out0 (portB<8>)
              (muxed thru external pin like SPI port pins)

    Outputs:
    dout    - SPI MISO
    nco_clk - NCO clock input
    swN     - one-hot mux NMOS control
    swP     - one-cold mux PMOS control
    tuneN   - IDAC switches
    tuneP   - IDAC complementary switches
    """

    N = 16
    N_DATA_BITS = 2*16 

    # SPI
    cdata = Signal(intbv(0)[N_DATA_BITS:])
    spiSlave = SPISlave(N_DATA_BITS, reset, scl, cs, din, dout, cdata)

    # pull out slices of SPI words

    cal = cdata(47)
    rst = cdata(46)
    seA = cdata(29)
    seB = cdata(13)
    fcw = cdata(46,32)

    mux0 = cdata(16)
    #buffer0
    mode0 = cdata(16,13)
    fast0 = cdata(12)
    tune0n = cdata(12,0)

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

