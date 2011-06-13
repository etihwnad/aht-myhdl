#!/usr/bin/env python

from myhdl import *


ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

def SwitchCtl(mult, cal, se, sw):
    """TX gate multiplier control
    
    mult    - 0=+1, 1=-1
    cal     - 0:normal, 1:short inputs to CM
    se      = 0:diff, 1:feedback

    Switch control outputs, 1 == on
    a       - ina-siga switch
    b       - inb-siga switch
    c       - ina-sigb switch
    d       - inb-sigb switch
    e       - cm-siga
    f       - cm-sigb
    g       - out-sigb
    """

    #@always(mult.posedge, mult.negedge)
    @always_comb
    def logic():
        if cal == 0:
            # normal +-1 diff mult
            if se == 0:
                if mult:
                    sw.next = 0b0110000
                else:
                    sw.next = 0b1001000
                #sw[6] = not mult
                #sw[5] = mult
                #sw[4] = mult
                #sw[3] = not mult
                #sw[2] = 0
                #sw[1] = 0
                #sw[0] = 0

            # SE mult of A only, B-out
            else:
                if mult:
                    sw.next = 0b0100001
                else:
                    sw.next = 0b1000001
                #sw[6] = not mult
                #sw[5] = mult
                #sw[4] = 0
                #sw[3] = 0
                #sw[2] = 0
                #sw[1] = 0
                #sw[0] = 1

        else:
            # Calibrate to CM open-loop
            if se == 0:
                sw.next = 0b0000110
                #sw[6] = 0
                #sw[5] = 0
                #sw[4] = 0
                #sw[3] = 0
                #sw[2] = 1
                #sw[1] = 1
                #sw[0] = 0

            # Calibrate to CM closed-loop
            else:
                sw.next = 0b0000101
                #sw[6] = 0
                #sw[5] = 0
                #sw[4] = 0
                #sw[3] = 0
                #sw[2] = 1
                #sw[1] = 0
                #sw[0] = 1

    return instances()


