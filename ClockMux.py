#!/usr/bin/env python

"""
Idea from: Techniques to make clock switching glitch free
           by Rafey Mahmud

http://www.eetimes.com/electronics-news/4138692/Techniques-to-make-clock-switching-glitch-free

Adapted to arbitrary number of inputs.
"""

import sys
from math import ceil, log

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1


def ClockMux(N, reset, sel, in_clocks, out_clock):
    """Glitch-free clock multiplexer
    
    N       - number of clocks

    reset   - async actLow reset
    sel     - clock select index
    in_clocks - vector of input clock lines

    Outputs:
    out_clock   - selected output clock
    """
    
    assert int(ceil(log(N, 2))) == len(sel)

    # internal signals 
    in_enables = [Signal(intbv(0)[0]) for i in range(N)]
    out_enables = [Signal(intbv(0)[0]) for i in range(N)]
    sync_clocks = [Signal(intbv(0)[0]) for i in range(N)]
    sync_clocks_concat = ConcatSignal(*reversed(sync_clocks))


    def Synchronizer(reset, clk_in, en_in, en_out, clk_out):
        """Single synchronizer stage.  Only enables clock iff en is asserted,
        which is iff it is the only one asserted.

        clk_in  - input clock
        en      - enable this clock

        not_en  - delayed, inverted enable
        """
        d0, d1 = [Signal(intbv(0)[0]) for i in range(2)]

        @always(clk_in.posedge, reset.negedge)
        def stage0():
            if reset == ACTIVE_LOW:
                d0.next = 0
            else:
                d0.next = en_in

        @always(clk_in.negedge, reset.negedge)
        def stage1():
            if reset == ACTIVE_LOW:
                en_out.next = 0
            else:
                en_out.next = d0

        @always_comb
        def clkOut():
            clk_out.next = (en_out and clk_in)

        return instances()

    
    def EnableLogic(index, sel, en):
        """Exclusive enable
        output = en and (not any(others))
        """
        them = [out_enables[j] for j in range(N) if j != i]
        if len(them) == 1:
            others = them[0]
        else:
            others = ConcatSignal(*reversed(them))
        @always_comb
        def enLogic():
            if ((sel == index) and 
                (others == 0)):
                en.next = 1
            else:
                en.next = 0
        return instances()

    #make the exclusive-enable combinational blocks
    enableBlocks = []
    for i in range(N):
        enableBlocks.append(EnableLogic(i, sel, in_enables[i]))

    #make the synchronizers
    syncBlocks = []
    for i in range(N):
        syncBlocks.append(
                Synchronizer(
                    reset,
                    in_clocks(i),
                    in_enables[i],
                    out_enables[i],
                    sync_clocks[i]
                    )
                )

    @always_comb
    def clockOr():
        out_clock.next = (sync_clocks_concat != 0) # OR of all vectors

    return instances()


def convert():
    N = 3
    reset = Signal(intbv(0)[0])
    sel = Signal(intbv(0)[2:])
    in_clocks = Signal(intbv(0)[N:])
    out_clock = Signal(intbv(0)[0])

    toVerilog(ClockMux, N, reset, sel, in_clocks, out_clock)


if __name__ == '__main__':
    convert()
