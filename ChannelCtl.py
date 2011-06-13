#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from NCO import NCO
from SPISlave import SPISlave
from SwitchCtl import SwitchCtl

def ChannelCtl(cal, mult, se, sw):
    """Channel digital control
    
    cal     - calibrate mode
    mult    - NCO output
    cdata  - 4b-switches, 12b-tuning

    sw     - TX gate mult switches
    cint   - Cap on
    zero   - Reset cap to Vcm
    fast   - gm x10
    tune   - 12bit IDAC word
    """

    #isw = Signal(intbv(0)[7:])

    # breakout channel signals
    #icint = cdata(15)
    #izero = cdata(14)
    #ise   = cdata(13)
    #ifast = cdata(12)
    #itune = cdata(12, 0)

    #
    # Multiplier/switch control
    #
    switchesCtl = SwitchCtl(mult, cal, se, sw)

    #@always_comb
    #def passthru():
        ##cint.next = icint
        ##zero.next = izero
        ##fast.next = ifast
        ##tune.next = itune
        #sw.next = isw

    return instances()


