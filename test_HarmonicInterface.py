
import os
from random import randrange
from math import ceil, floor

from myhdl import *

from HarmonicInterface import HarmonicInterface
from test_SPISlave import start, stop, sendBit, tx


PERIOD = 10


# system clock, e.g. NS430 cpu clock
sysclk = Signal(bool(0))

counter = Signal(intbv(0))

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

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def fcw2period(fcw, N):
    return float(2**N) / fcw

# get a harmonic instance
def mkharmonic():
    return  HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp)

class SPI: pass
spi = SPI()
spi.clk = sysclk
spi.scl = scl_in
spi.cs = cs_in
spi.din = din
spi.dout = dout

class HarmonicVector:
    bitpos = {
            'cal':slice(48,47),
            'rst':slice(47,46),
            'fcw':slice(46,32),
            'cintA':slice(32,31),
            'zeroA':slice(31,30),
            'seA':slice(30,29),
            'fastA':slice(29,28),
            'tuneA':slice(28,16),
            'cintB':slice(16,15),
            'zeroB':slice(15,14),
            'seB':slice(14,13),
            'fastB':slice(13,12),
            'tuneB':slice(12,0)
            }

    def __init__(self, data=0):
        self.__dict__['data'] = intbv(data)[48:]

    def __setattr__(self, name, value):
        if name == 'data':
            self.__dict__['data'] = intbv(value)[48:]
        elif name not in self.bitpos:
            raise KeyError('%s is not a valid element' % name)
        else:
            self.__dict__['data'][self.bitpos[name]] = intbv(value)

    def __getattr__(self, name):
        if name in self.bitpos:
            return self.data[self.bitpos[name]]



@always(delay(PERIOD//2))
def sysclock():
    sysclk.next = not sysclk


N_DATA_BITS = 48
class TestSingleHarmonic:
    def sysreset(self):
        reset_in.next = 0
        yield sysclk.posedge
        reset_in.next = 1
        yield sysclk.posedge

    def bench_spi_shift(self):
        harmonic = mkharmonic()
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
        harmonic = mkharmonic()
        @instance
        def check():
            for i in range(2**4):
                i = intbv(i)

                sysclock.next = 0
                yield self.sysreset()

                clk_in.next = i[3]
                scl_in.next = i[2]
                reset_in.next = i[1]
                cs_in.next = i[0]
                yield sysclk.posedge

                assert clk_out == clk_in
                assert scl_out == scl_in
                assert reset_out == reset_in
                assert cs_out == cs_in
            raise StopSimulation
        return sysclock, harmonic, check

    def test_spi_passthru(self):
        sim = Simulation(self.bench_spi_passthru())
        sim.run()

    def bench_spi_tune(self):
        harmonic = mkharmonic()
        @instance
        def check():
            for trial in range(10):
                indata = intbv(randrange(2**N_DATA_BITS))[N_DATA_BITS:]
                invec = HarmonicVector(indata)
                yield self.sysreset()
                yield tx(spi, indata)

                assert invec.tuneA == tuneAn
                assert invec.tuneA == ~tuneAp
                assert invec.tuneB == tuneBn
                assert invec.tuneB == ~tuneBp
                assert invec.cintA == cintAn
                assert invec.cintA == (not cintAp)
                assert invec.zeroA == zeroAn
                assert invec.zeroA == (not zeroAp)
                assert invec.fastA == fastAn
                assert invec.fastA == (not fastAp)
                assert invec.cintB == cintBn
                assert invec.cintB == (not cintBp)
                assert invec.zeroB == zeroBn
                assert invec.zeroB == (not zeroBp)
                assert invec.fastB == fastBn
                assert invec.fastB == (not fastBp)
            raise StopSimulation
        return sysclock, harmonic, check
            
    def test_spi_tune(self):
        sim = Simulation(self.bench_spi_tune())
        sim.run()


    def make_bench_spi_nco(self, fcw):
        # connect NCO to switches
        harmonic = HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
            nco_i, nco_q, nco_i, nco_q,
            clk_out, reset_out, scl_out, cs_out, dout,
            swAp, swAn,
            cintAn, zeroAn, fastAn, tuneAn,
            cintAp, zeroAp, fastAp, tuneAp,
            swBp, swBn,
            cintBn, zeroBn, fastBn, tuneBn,
            cintBp, zeroBp, fastBp, tuneBp)

        a,b,c,d,e,f,g = downrange(7)

        swAb = swAn(b)
        swBb = swBn(b)
    
        @always(delay(5*PERIOD))
        def ncoclock():
            clk_in.next = not clk_in

        @always(clk_in.posedge)
        def cnt():
            counter.next = counter + 1


        foundA = Signal(bool(0))
        lastA = Signal(intbv(0))
        @always(swAb.negedge)
        def monitorA():
            if lastA > counter:
                foundA.next = False
            elif lastA != 0:
                ideal = fcw2period(fcw, 16)
                period = counter - lastA
                assert (period == int(floor(ideal)) or
                        period == int(ceil(ideal)))
                foundA.next = True
            lastA.next = counter

        foundB = Signal(bool(0))
        lastB = Signal(intbv(0))
        @always(swBb.negedge)
        def monitorB():
            if lastB > counter:
                foundB.next = False
            elif lastB != 0:
                ideal = fcw2period(fcw, 16)
                period = counter - lastB
                assert (period == int(floor(ideal)) or
                        period == int(ceil(ideal)))
                foundB.next = True
            lastB.next = counter

        @instance
        def control():
            #lastB.next = 0
            yield self.sysreset()
            invec = HarmonicVector(0)
            invec.cal = 0 #no calibration
            invec.rst = 1
            invec.fcw = fcw
            counter.next = 0
            print 'indata:', bin(invec.data, 48)
            #yield self.sysreset()
            yield tx(spi, invec.data)
            invec.rst = 1 #run the NCO
            yield tx(spi, invec.data)
            counter.next = 0

            print 'fcw:', bin(invec.fcw, 14), invec.fcw
            # run for master period
            GRR = 2**16 / gcd(invec.fcw, 2**16)
            print 'GRR:', GRR
            for i in range(GRR):
                yield clk_in.negedge

            for i in range(int(fcw2period(fcw, 16))):
                if foundA and foundB:
                    break
                yield clk_in.negedge

            #ensure we actually found edges...
            assert foundA
            assert foundB
            raise StopSimulation
        return (sysclock, harmonic, ncoclock, cnt,
                monitorA, monitorB, control)

    def test_spi_nco(self):
        for fcw in [2**14-1, 2**13-4, 2**12, 2**8] +  [-1]*3]:
            if fcw == -1:
                fcw = randrange(2**14)
            tb = self.make_bench_spi_nco(fcw)
            sim = Simulation(tb)
            sim.run()


if __name__ == '__main__':
    #TestSingleHarmonic().test_spi_shift()
    #TestSingleHarmonic().test_spi_passthru()
    TestSingleHarmonic().test_spi_nco()



