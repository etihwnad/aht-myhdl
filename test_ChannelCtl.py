
from myhdl import *

from ChannelCtl import ChannelCtl

PERIOD = 10

cal, mult = [Signal(bool(0)) for i in range(2)]
cdata = Signal(intbv(0)[16:])

sw = Signal(intbv(0)[7:])
cint = Signal(bool(0))
fast = Signal(bool(0))
zero = Signal(bool(0))
tune = Signal(intbv(0)[12:])





def bench_ChannelCtl():
    harmonic = ChannelCtl(cal, mult, cdata,
        sw) #, cint, zero, fast, tune,
        #)

    @always(delay(PERIOD//2))
    def multgen():
        mult.next = not mult



    @instance
    def transaction():
        cal.next = 0
        cdata.next = 0b0000100010000000
        for i in range(10):
            yield mult.negedge

        cal.next = 0
        cdata.next = 0b0010100010000000
        for i in range(10):
            yield mult.negedge

        cal.next = 1
        cdata.next = 0b1010100010000000
        for i in range(2):
            yield mult.negedge

        cal.next = 1
        cdata.next = 0b1000100010000000
        for i in range(2):
            yield mult.negedge

        raise StopSimulation

    return instances()


def test_bench_ChannelCtl():
    tracer = traceSignals(bench_ChannelCtl)
    sim = Simulation(tracer)
    sim.run()


def convert():
    toVerilog.header = '''
parameter True=1;
parameter False=0;
'''
    toVerilog(ChannelCtl,
        cal, mult, cdata,
        sw) #, cint, zero, fast, tune
        #)


if __name__ == '__main__':
    convert()





