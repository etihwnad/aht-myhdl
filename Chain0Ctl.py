#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from SPISlave import SPISlave
from AnalogMuxCtl import AnalogMuxCtl
from BufferCtl import BufferCtl

N = 16
N_DATA_BITS = 16 + 2*16 
N_MUX_INPUTS = 49 #48 harmonics + CMI

def Chain0Ctl(
        reset, scl, cs, din,
        dout,
        txAn, txAp,
        txBn, txBp,
        swAn, swAp,
        swBn, swBp,
        fastAn, fastAp,
        fastBn, fastBp,
        tuneAn, tuneAp,
        tuneBn, tuneBp):
    """Harmonic chain 0 multiplexer and pad buffer control

    Inputs:
    reset   - reset SPI register
    scl     - SPI SCLK
    cs      - SPI CS
    din     - SPI MOSI

    Outputs:
    dout    - SPI MISO
    txXn    - one-hot mux A/B NMOS control
    txXn    - one-cold mux A/B PMOS control
    swXn    - buffer A/B mode NMOS switches
    swXp    - buffer A/B mode PMOS switches
    fastXn  - buffer A/B gm config
    fastXp  - buffer A/B gm config
    tuneXn  - IDAC A/B switches
    tuneXp  - IDAC A/B complementary switches
    """


    # SPI
    cdata = Signal(intbv(0)[N_DATA_BITS:])
    spiSlave = SPISlave(N_DATA_BITS, reset, scl, cs, din, dout, cdata)

    # pull out slices of SPI words
    unusedA  = cdata(48,46)
    muxSelA  = cdata(46,40)

    unusedB  = cdata(40,38)
    muxSelB  = cdata(38,32)

    bufModeA = cdata(32,29)
    fastA    = cdata(28)
    tuneA    = cdata(28,16)

    bufModeB = cdata(16,13)
    fastB    = cdata(12)
    tuneB    = cdata(12,0)


    # Analog Mux
    tAn, tAp, tBn, tBp = [Signal(intbv(0)[N_MUX_INPUTS:]) for i in range(4)]
    muxA = AnalogMuxCtl(N_MUX_INPUTS, 0, muxSelA, tAn, tAp)
    muxB = AnalogMuxCtl(N_MUX_INPUTS, 0, muxSelB, tBn, tBp)

    # Buffer switch control
    sA, sB = [Signal(intbv(0)[4:]) for i in range(2)]
    bufSwCtlA = BufferCtl(bufModeA, sA)
    bufSwCtlB = BufferCtl(bufModeB, sB)


    @always_comb
    def muxbits():
        txAn.next = tAn
        txAp.next = tAp
        txBn.next = tBn
        txBp.next = tBp

    @always(cdata)
    def passthru():
        swAn.next = sA
        swAp.next = ~sA

        swBn.next = sB
        swBp.next = ~sB

        fastAn.next = fastA
        fastAp.next = not fastA

        fastBn.next = fastB
        fastBp.next = not fastB

        tuneAn.next = tuneA
        tuneAp.next = ~tuneA

        tuneBn.next = tuneB
        tuneBp.next = ~tuneB


    return instances()


def convert():
    reset, scl, cs, din, dout = [Signal(intbv(0)[0]) for i in range(5)]
    txAn, txAp, txBn, txBp = [Signal(intbv(0)[N_MUX_INPUTS:]) for i in range(4)]
    swAn, swAp, swBn, swBp = [Signal(intbv(0)[4:]) for i in range(4)]
    fastAn, fastAp, fastBn, fastBp = [Signal(intbv(0)[0]) for i in range(4)]
    tuneAn, tuneAp, tuneBn, tuneBp = [Signal(intbv(0)[12:]) for i in range(4)]

    toVerilog(
        Chain0Ctl,
        reset, scl, cs, din,
        dout,
        txAn, txAp,
        txBn, txBp,
        swAn, swAp,
        swBn, swBp,
        fastAn, fastAp,
        fastBn, fastBp,
        tuneAn, tuneAp,
        tuneBn, tuneBp)

if __name__ == '__main__':
    convert()

