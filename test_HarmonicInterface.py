
import os
from random import randrange

from myhdl import *

from HarmonicInterface import HarmonicInterface
from test_SPISlave import start, stop, sendBit, tx


PERIOD = 10


# system clock, e.g. NS430 cpu clock
sysclk = Signal(bool(0))

# harmonic digital lines
clk_in, reset_in, scl_in, cs_in = [Signal(intbv(0)[0]) for i in range(4)]
clk_out, reset_out, scl_out, cs_out = [Signal(intbv(0)[0]) for i in range(4)]
din, dout = [Signal(intbv(0)[0]) for i in range(2)]
nco_i, nco_q = [Signal(intbv(0)[0]) for i in range(2)]
multA, multB = [Signal(intbv(0)[0]) for i in range(2)]

swAn = Signal(intbv(0)[7:])
swAp = Signal(intbv(0)[7:])
swBn = Signal(intbv(0)[7:])
swBp = Signal(intbv(0)[7:])

cintAn, zeroAn, fastAn = [Signal(intbv(0)[0]) for i in range(3)]
cintAp, zeroAp, fastAp = [Signal(intbv(0)[0]) for i in range(3)]

cintBn, zeroBn, fastBn = [Signal(intbv(0)[0]) for i in range(3)]
cintBp, zeroBp, fastBp = [Signal(intbv(0)[0]) for i in range(3)]

tuneAn = Signal(intbv(0)[12:])
tuneAp = Signal(intbv(0)[12:])

tuneBn = Signal(intbv(0)[12:])
tuneBp = Signal(intbv(0)[12:])

# get a harmonic instance
harmonic = HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
    nco_i, nco_q, multA, multB,
    clk_out, reset_out, scl_out, cs_out, dout,
    swAp, swAn,
    cintAn, zeroAn, fastAn, tuneAn,
    cintAp, zeroAp, fastAp, tuneAp,
    swBp, swBn,
    cintBn, zeroBn, fastBn, tuneBn,
    cintBp, zeroBp, fastBp, tuneBp)

class SPI:
    pass

spi = SPI()
spi.clk = sysclk
spi.scl = scl_in
spi.cs = cs_in
spi.din = din
spi.dout = dout

@always(delay(PERIOD//2))
def sysclock():
    sysclk.next = not sysclk
    print sysclk


N_DATA_BITS = 48
class TestSingleHarmonic:
    def sysreset(self):
        reset_in.next = 0
        yield sysclk.posedge
        reset_in.next = 1
        yield sysclk.posedge

    def bench_spi_shift(self):
        @instance
        def check():
            # a batch of random inputs
            for trial in range(10):
                collector = intbv(0)[N_DATA_BITS:]
                indata = intbv(randrange(2**N_DATA_BITS))[N_DATA_BITS:]

                yield self.sysreset()

                yield tx(spi, indata)

                # shift out data
                yield start(spi)
                for i in downrange(N_DATA_BITS):
                    collector[i] = dout
                    yield sendBit(spi, 0)
                yield stop(spi)
                assert collector == indata
            raise StopSimulation
        return sysclock, harmonic, check

    def test_spi_shift(self):
        sim = Simulation(self.bench_spi_shift())
        sim.run()

    def bench_spi_passthru(self):
        @instance
        def check():
            for i in range(10):
                sysclock.next = 0
                yield self.sysreset()

                clk_in.next = randrange(2)
                scl_in.next = randrange(2)
                reset_in.next = randrange(2)
                cs_in.next = randrange(2)
                yield sysclk.posedge
                yield sysclk.posedge
                print map(bin, [clk_in, scl_in, reset_in, cs_in])
                print map(bin, [clk_out, scl_out, reset_out, cs_out])

                assert clk_out == clk_in
                assert scl_out == scl_in
                assert reset_out == reset_in
                assert cs_out == cs_in
            raise StopSimulation
        return sysclock, harmonic, check

    def test_spi_passthru(self):
        sim = Simulation(self.bench_spi_passthru())
        sim.run()

            







## test vector to send in via SPI
#indata = Signal(intbv(0)[3*16:])
#
#def start():
#    scl_in.next = 0
#    cs_in.next = 0
#    yield clk_in.negedge
#
#def sendBit(b):
#    scl_in.next = 0
#    din.next = b
#    yield delay(2)
#    scl_in.next = 1
#    yield clk_in.negedge
#
#def stop():
#    scl_in.next = 0
#    cs_in.next = 1
#    yield clk_in.negedge
#
#def spi_tx(word, n):
#    yield start()
#    for i in downrange(n):
#        yield sendBit(word[i])
#    yield stop()
#
#
#def bench_HarmonicInterface():
#    harmonic = HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
#        nco_i, nco_q, multA, multB,
#        clk_out, reset_out, scl_out, cs_out, dout,
#        swAp, swAn,
#        cintAn, zeroAn, fastAn, tuneAn,
#        cintAp, zeroAp, fastAp, tuneAp,
#        swBp, swBn,
#        cintBn, zeroBn, fastBn, tuneBn,
#        cintBp, zeroBp, fastBp, tuneBp)
#
#    @always_comb
#    def wires():
#        """Connect NCO to multiplier"""
#        multA.next = nco_i
#        multB.next = nco_q
#
#    @always(delay(PERIOD//2))
#    def clkgen():
#        clk_in.next = not clk_in
#
#
#    @instance
#    def transaction():
#        reset_in.next = 1
#        yield clk_in.negedge
#
#        reset_in.next = 0
#        yield clk_in.negedge
#
#        reset_in.next = 1
#        yield clk_in.negedge
#
#        #                               /  channel A   \/  channel B   \
#        #               cr/   fcw      \czsf/ tuneA    \czsf/ tuneA    \
#        indata.next = 0b010101000000000010101000100000000101100001111111
#        yield spi_tx(indata, 48)
#
#        cs_in.next = 0
#        for i in range(1000):
#            yield clk_in.negedge
#
#        #                               /  channel A   \/  channel B   \
#        #               cr/   fcw      \czsf/ tuneA    \czsf/ tuneA    \
#        indata.next = 0b010001011000100100001010100000001110100010111111
#        yield spi_tx(indata, 48)
#        #yield spi_tx(indata, 48)
#        for i in range(1000):
#            yield clk_in.negedge
#
#        for i in range(10):
#            yield clk_in.negedge
#
#        raise StopSimulation
#
#    return instances()
#
#
#
#
#
#def _test_bench_HarmonicInterface():
#    tracer = traceSignals(bench_HarmonicInterface)
#    sim = Simulation(tracer)
#    sim.run()
#
#
if __name__ == '__main__':
    TestSingleHarmonic().test_spi_shift()
    TestSingleHarmonic().test_spi_passthru()


