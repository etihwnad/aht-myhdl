#!/usr/bin/env python

from myhdl import *

import sys

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1


def SPISlave(N, reset, scl, cs, din, dout, data):
    """Harmonic digital control
    
    reset   - async reset to default values
    scl     - input clock
    cs      - Chip Select: low:shift in data, high:latch to outputs
    din     - serial data in
    dout    - serial data out

    data    - latched data (read-only)
    """

    reg = Signal(intbv(0)[N:])
    sample = Signal(intbv(0)[0])

    @always(scl.posedge, scl.negedge, reset.negedge)
    def InputRegister():
        if reset == ACTIVE_LOW:
            reg.next = 0
        elif cs == ACTIVE_LOW:
            #sample on sck rising edge
            if scl == ACTIVE_HIGH:
                sample.next = din
            #shift on falling edge
            elif scl == ACTIVE_LOW:
                reg.next[N:1] = reg[N-1:]
                reg.next[0] = sample

        # correct out data always available
        dout.next = reg.next[N-1]

    @always(cs.posedge)
    def ChipSelect():
        if cs == ACTIVE_HIGH:
            data.next = reg

    return instances()
