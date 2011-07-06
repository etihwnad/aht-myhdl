#!/usr/bin/env python

from math import ceil, log

from myhdl import *


def AnalogMuxCtl(N, default, sel, swN, swP):
    """TX gate multiplexer control
    
    Construction:
    N       - N switches (constructor)
    default - output if sel>=N

    Inputs:
    sel     - ceil(log2(N))-bit selector

    Outputs:
    swN     - N-long one-hot output vector for NMOS switches
    swP     - N-long one-cold output vector for PMOS switches
    """

    Nbits = int(ceil(log(N, 2)))
    SELECTOR = [2**i for i in range(N)]
    
    #SELECTOR.append(int(default))
    # explicitly fill in unused cases with default value
    for i in range(N, 2**Nbits):
        SELECTOR.append(int(default))

    SELECTOR = tuple(SELECTOR)

    x = Signal(intbv(0)[N:])

    @always_comb
    def logic():
        x.next = SELECTOR[sel]

    @always_comb
    def outputs():
        swN.next = x
        swP.next = ~x

    return instances()
    #return muxCtl


def convert():
    N = 48
    Nbits = ceil(log(N, 2))
    default = intbv(0)[Nbits:]

    sel = Signal(intbv(0)[Nbits:])
    swN = Signal(intbv(0)[N:])
    swP = Signal(intbv(0)[N:])

    toVerilog(AnalogMuxCtl, N, default, sel, swN, swP)

if __name__ == '__main__':
    convert()

