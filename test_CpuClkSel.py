#!/usr/bin/env python

from myhdl import *

from CpuClkSel import CpuClkSel

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1



def test_mode00():
    """HF enabled, HF selected"""
    reset = Signal(intbv(0)[0])
    sel = Signal(intbv(0)[2:])
    hfxtal = Signal(bool(0))
    lfxtal = Signal(bool(0))
    hf_en = Signal(intbv(0)[0])
    cpu_clk = Signal(bool(0))

    clkSel = CpuClkSel(reset, sel, hfxtal, lfxtal, hf_en, cpu_clk)

    @always(delay(2))
    def hfclk():
        hfxtal.next = not hfxtal

    @always(delay(7))
    def lfclk():
        lfxtal.next = not lfxtal

    @instance
    def test():
        reset.next = 1
        sel.next = 0b00
        yield hfxtal.posedge
        yield lfxtal.posedge
        yield lfxtal.posedge
        yield hfxtal.posedge

        for i in range(10):
            yield hfxtal.posedge
            assert hf_en == 1
            assert hfxtal == cpu_clk


def test_mode01():
    """HF enabled, LF selected"""
    reset = Signal(intbv(0)[0])
    sel = Signal(intbv(0)[2:])
    hfxtal = Signal(bool(0))
    lfxtal = Signal(bool(0))
    hf_en = Signal(intbv(0)[0])
    cpu_clk = Signal(bool(0))

    clkSel = CpuClkSel(reset, sel, hfxtal, lfxtal, hf_en, cpu_clk)

    @always(delay(2))
    def hfclk():
        hfxtal.next = not hfxtal

    @always(delay(7))
    def lfclk():
        lfxtal.next = not lfxtal

    @instance
    def test():
        reset.next = 1
        sel.next = 0b01
        yield hfxtal.posedge
        yield lfxtal.posedge
        yield lfxtal.posedge
        yield hfxtal.posedge

        for i in range(10):
            yield lfxtal.posedge
            assert hf_en == 1
            assert lfxtal == cpu_clk


def test_mode10_11():
    """HF disabled, LF selected"""
    reset = Signal(intbv(0)[0])
    sel = Signal(intbv(0)[2:])
    hfxtal = Signal(bool(0))
    lfxtal = Signal(bool(0))
    hf_en = Signal(intbv(0)[0])
    cpu_clk = Signal(bool(0))

    clkSel = CpuClkSel(reset, sel, hfxtal, lfxtal, hf_en, cpu_clk)

    @always(delay(2))
    def hfclk():
        hfxtal.next = not hfxtal

    @always(delay(7))
    def lfclk():
        lfxtal.next = not lfxtal

    @instance
    def test():
        reset.next = 1
        for s in [0b10, 0b11]:
            sel.next = s
            yield hfxtal.posedge
            yield lfxtal.posedge
            yield lfxtal.posedge
            yield hfxtal.posedge

            for i in range(10):
                yield lfxtal.posedge
                assert hf_en == 0
                assert lfxtal == cpu_clk



