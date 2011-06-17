#!/usr/bin/env python

from myhdl import *

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

def NCO(N, clk, reset, rst, fcw, outi, outq):
    """Numerically controlled oscillator.
    
    N       - phase accumulator bit-width CONFIG
    clk     - clock input
    reset   - global actLow asynchronous reset-to-zero
    rst     - local reset-to-zero
    fcw     - phase increment tuning word
    outi    - in-phase output
    outq    - quadrature output
    """
    assert(N >= 2)

    acc_max = 2**N
    offset = 2**(N-2)

    MSB = N-1

    phase = Signal(intbv(0)[N:])
    phase_delay = Signal(intbv(0)[N:])
    x = Signal(intbv(0)[N:])

    @always(clk.negedge)
    def loopdelay():
        if reset == ACTIVE_LOW:
            phase_delay.next = 0
        else:
            phase_delay.next = phase

    @always(clk.posedge, reset.negedge)
    def ncoLogic():
        if reset == ACTIVE_LOW:
            phase.next = 0
            outi.next = 0
            outq.next = 0
        elif rst == ACTIVE_LOW:
            phase.next = 0
            outi.next = 0
            outq.next = 0
        else:
            phase.next = (phase_delay + fcw) % acc_max
            tmp = (phase_delay + offset) % acc_max
            outi.next = intbv(tmp)[MSB]
            outq.next = phase[MSB]

    return instances()


