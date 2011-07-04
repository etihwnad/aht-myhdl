import itertools
from math import ceil, log
import random

from myhdl import *

from ClockMux import ClockMux



def test_noGlitches():
    def bench_ClockMux_noGlitches():
        N = 4
        Nbits = int(ceil(log(N, 2)))
        clk_half_periods = [random.randrange(1, 10*N) for i in range(N)]
        print 'half-periods:', clk_half_periods
        
        reset = Signal(bool(0))
        sel = Signal(intbv(0)[Nbits:])
        clocks = [Signal(bool(0)) for i in range(N)]
        #convert to a bitvector
        in_clocks = ConcatSignal(*reversed(clocks))
        clk = Signal(bool(0))

        mux = ClockMux(N, reset, sel, in_clocks, clk)

        # bank of clock generators
        def mkClockGen(t, ck):
            @always(delay(t))
            def clkgen():
                ck.next = not ck
            return clkgen

        clkgens = []
        for i in range(N):
            clkgens.append(mkClockGen(clk_half_periods[i], clocks[i]))

        # select each clock and run for awhile
        @instance
        def selector():
            # every clock-switching combination
            reset.next = 1
            for i in [item for sublist in itertools.combinations(range(N), 2)
                           for item in sublist]:
                sel.next = i
                #run for at at least 4 periods
                yield delay(2*4*max(clk_half_periods))
                #make select signal asynchronous with clocks
                yield delay(random.randrange(min(clk_half_periods)))
            reset.next = 0
            yield delay(10)
            reset.next = 1
            yield delay(1000)
            raise StopSimulation

        # any edge-to-edge clk length shorter than the smallest clock half-period
        # is a glitch
        global last_time
        last_time = 0
        @always(clk)
        def monitor():
            global last_time
            this_time = now()
            width = this_time - last_time
            assert width >= min(clk_half_periods)
            last_time = this_time

        return instances() #mux, clkgens, selector, monitor

    tb = traceSignals(bench_ClockMux_noGlitches)
    sim = Simulation(tb)
    sim.run()


if __name__ == '__main__':
    test_noGlitches()

