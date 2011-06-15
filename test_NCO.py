#!/usr/bin/env python

from math import ceil, floor
from myhdl import *

ACTIVE_HIGH, INACTIVE_LOW = 1,0
ACTIVE_LOW, INACTIVE_HIGH = 0,1

from NCO import NCO


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


CLKPERIOD = 10


def fcw2period(fcw, N):
    return float(2**N) / fcw

def test_period():
    def test(tune, N):
        clk, reset, rst = [Signal(bool(0)) for i in range(3)]
        outi = Signal(intbv(0)[0])
        outq = Signal(intbv(0)[0])
        fcw = Signal(intbv(0)[N-2:])

        counter = Signal(intbv(0)[N+1:])

        dut = NCO(N, clk, reset, rst, fcw, outi, outq)

        @always(delay(CLKPERIOD//2))
        def clockgen():
            clk.next = not clk

        @always(clk.posedge)
        def count():
            counter.next = counter + 1
            #print bin(outi), bin(outq)

        #
        # measure I/Q periods at falling edges
        #
        # Actual period is the interger above or below avg period
        last_i = Signal(intbv(0))
        @always(outi.negedge)
        def monitor_i():
            if last_i != 0:
                ideal = fcw2period(fcw, N)
                period = counter - last_i
                assert (period == int(floor(ideal)) or
                        period == int(ceil(ideal)))
            last_i.next = counter

        last_q = Signal(intbv(0))
        @always(outq.negedge)
        def monitor_q():
            if last_q != 0:
                ideal = fcw2period(fcw, N)
                period = counter - last_q
                assert (period == int(floor(ideal)) or
                        period == int(ceil(ideal)))
            last_q.next = counter

        @instance
        def control():
            GRR = 2**N / float(gcd(tune, 2**N))
            print 'GRR:', GRR
            GRR = int(GRR)

            fcw.next = tune
            reset.next = 1
            rst.next = 1
            yield clk.negedge

            #reset to zero
            reset.next = 0
            rst.next = 0
            yield clk.negedge

            # go
            reset.next = 1
            rst.next = 1
            counter.next = 0
            yield clk.negedge

            yield delay(CLKPERIOD * (GRR + 1))
            #tested complete true period
            raise StopSimulation

        return instances()

    N = 16
    for tune in (1, 2, 16, 17, 32, 64, 2**(N-2)-1):
        print '---------------------------'
        print 'tune:', tune
        print 'avg period:', fcw2period(tune, N)

        def bench_NCO_period():
            return test(tune, N)
        check = test(tune, N)
        #trace = traceSignals(bench_NCO_period)
        sim = Simulation(bench_NCO_period())
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
    #test_period()


