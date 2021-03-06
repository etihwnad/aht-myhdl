#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

def BufferCtl(mode, sw):
    """TX gate multiplier control
    
    cint    - unused
    zero    - +input to CMI
    se      = 0:openloop, 1:follower

    mode    - [cint, zero, se] bit vector (as integer)

    Switch control outputs, 1 == on
    a       - mux-inA
    b       - CMI-inA
    c       - CMI-inB
    d       - inB-out
    """

    # mode[2] is unused, don't care
    # only mode[1:0] used
    MODE_SWITCHES = (
            0b1010, #mux cmp
            0b1010, #mux cmp

            0b1001, #mux buff
            0b1001, #mux buff

            0b0110, #tune fast
            0b0110, #tune fast

            0b0101, #tune slow
            0b0101, #tune slow
            )

    @always_comb
    def logic():
        sw.next = MODE_SWITCHES[int(mode)]

    return instances()


def convert():
    mode = Signal(intbv(0)[3:])
    sw = Signal(intbv(0)[4:])

    toVerilog(BufferCtl, mode, sw)


if __name__ == '__main__':
    convert()
