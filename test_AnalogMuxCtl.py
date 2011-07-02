
from math import log, ceil
from myhdl import *


from AnalogMuxCtl import AnalogMuxCtl


CLKPERIOD = 10

# buffer register bits
# 15        cint/NotUsed
# 14        zero/tuneMode
# 13        se/buffer
# 12        fast
# [11:0]    tune


def test_oneHot():
    """Only one output selected"""
    N = 33
    Nbits = int(ceil(log(N, 2)))
    print N, Nbits

    #default state is all switches OFF
    default = intbv(-1)[N:]

    sel = Signal(intbv(0)[Nbits:])
    swN = Signal(intbv(0)[N:])
    swP = Signal(intbv(0)[N:])
    mux = AnalogMuxCtl(N, default, sel, swN, swP)

    def test():
        @instance
        def inst():
            expected = Signal(intbv(0)[N:])
            for i in range(N):
                print 'sel =', i, (1<<i)
                sel.next = i
                expected.next = (1 << i)
                yield delay(10)
                print bin(expected, N), bin(~expected, N)
                print bin(swN, N), bin(swP, N)
                assert intbv(swN.val, max=2**Nbits) == expected
                assert intbv(swP.val, max=2**Nbits) == ~expected

            for i in range(N, 2**Nbits):
                sel.next = i
                yield delay(10)
                assert swN == default
                assert swP == ~default
            raise StopSimulation
        return instances()
    sim = Simulation(mux, test())
    sim.run()


