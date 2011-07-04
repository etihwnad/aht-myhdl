#!/usr/bin/env python

from myhdl import *

from ClockMux import ClockMux

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

def CpuClkSel(reset, sel, hfxtal, lfxtal, hf_en, cpu_clk):
    """NS430 system clock select, HF enable
    
    reset   - Nrst system reset
    sel     - SysClkSel<1:0> from NS430
    hfxtal  - HF crystal output
    lfxtal  - 32k crystal output

    hf_en   - Enable HF crystal
    cpu_clk - Main clock for NS430
    """

    clk_sel = Signal(intbv(0)[0])
    in_clocks = Signal(intbv(0)[2:])

    @always_comb
    def cheat():
        in_clocks.next[0] = hfxtal
        in_clocks.next[1] = lfxtal

    clkMux = ClockMux(2, reset, clk_sel, in_clocks, cpu_clk)

    @always_comb
    def hf_en_logic():
        hf_en.next = ~sel[1]

    @always_comb
    def clk_sel_logic():
        if sel == 0:
            clk_sel.next = 0
        else:
            clk_sel.next = 1

    return instances()


def convert():
    reset = Signal(intbv(0)[0])
    sel = Signal(intbv(0)[2:])
    hfxtal = Signal(intbv(0)[0])
    lfxtal = Signal(intbv(0)[0])
    hf_en = Signal(intbv(0)[0])
    cpu_clk = Signal(intbv(0)[0])

    toVerilog(CpuClkSel, reset, sel, hfxtal, lfxtal, hf_en, cpu_clk)


if __name__ == '__main__':
    convert()

