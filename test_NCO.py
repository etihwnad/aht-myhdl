#!/usr/bin/env python

from myhdl import *

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from NCO import NCO


CLKPERIOD = 10

def bench_NCO():

    N = 16

    fcw = Signal(intbv(0)[N-2:])
    clk, reset, rst = [Signal(bool(0)) for i in range(3)]
    outi = Signal(intbv(0)[0])
    outq = Signal(intbv(0)[0])
    #outi.driven = True
    #outq.driven = True

    NCO_inst = NCO(N, clk, reset, rst, fcw, outi, outq)

    @always(delay(CLKPERIOD//2))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        fcw.next = 10
        reset.next = 1
        rst.next = 1

        for f, ncycles in ((10000, 100), (0x3fff, 100), (0x2000, 100)):
            fcw.next = f
            reset.next = 0
            yield clk.negedge

            reset.next = 1
            yield clk.negedge

            for i in range(ncycles):
                yield clk.negedge

            rst.next = 0
            for i in range(ncycles):
                yield clk.negedge

            rst.next = 1
            for i in range(ncycles):
                yield clk.negedge

        
        raise StopSimulation

    @instance
    def monitor():
        print 'r  fcw : i q'
        print '------------'
        
        while True:
            yield clk.negedge
            print '%1d %5d: %1d %1d' % \
                    (reset, fcw, outi, outq)

    return NCO_inst, clkgen, stimulus, monitor


def test_bench_NCO():
    tracer = traceSignals(bench_NCO)
    sim = Simulation(tracer)
    sim.run()


def convert():
    toVerilog.header = '''
parameter True=1;
parameter False=0;
'''

    N = 16

    fcw = Signal(intbv(0)[N-2:])
    clk, reset, rst = [Signal(bool(0)) for i in range(3)]
    pi = Signal(intbv(0)[0])
    pq = Signal(intbv(0)[0])

    toVerilog(NCO, N, clk, reset, rst, fcw, pi, pq)


if __name__ == '__main__':
    convert()
    #test_bench_NCO()


