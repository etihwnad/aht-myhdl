
import os
from random import randrange
from math import ceil, floor

from myhdl import *

from HarmonicInterface import HarmonicInterface as _HarmonicInterface
from test_SPISlave import start, stop, sendBit, tx

DEBUG = True

COSIM = os.getenv('MYHDL_COSIM')
if COSIM is None or COSIM == '0':
    COSIM = False
else:
    COSIM = True

SIMULATOR = 'iverilog'
#SIMULATOR = 'cver'


N_DATA_BITS = 48
PERIOD = 1000


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


def HarmonicInterface(
        clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp,
        cosim=False):
    if cosim:
        if SIMULATOR == 'iverilog':
            runcmd = "vvp -m ./myhdl.vpi.%s HarmonicInterface" % \
                    os.getenv('HOSTNAME')
            cmd0 = r"sed -e 's/endmodule/initial begin\n    $sdf_annotate(\"HarmonicInterface.sdf\", dut);\n        end\nendmodule/' < tb_HarmonicInterface.v > tb_HarmonicInterface.vnet"
            #cmd0 = "cp tb_HarmonicInterface.v tb_HarmonicInterface.vnet"
            cmd1 = "iverilog -gspecify -o HarmonicInterface \
                    ibm13rfrvt.v \
                    HarmonicInterface.vnet \
                    tb_HarmonicInterface.vnet"
                        
            print os.system(cmd0)
            print os.system(cmd1)

        elif SIMULATOR == 'cver':
                    #+change_port_type \
                    #+sdf_annotate HarmonicInterface.sdf+tb_HarmonicInterface.dut \
            runcmd = "cver -l HarmonicInterface.cver.log +typdelays \
                    +loadvpi=./myhdl.cver.twain.so:vpi_compat_bootstrap \
                    -informs \
                    +printstats \
                    -v ibm13rfrvt.v \
                    HarmonicInterface.vnet \
                    tb_HarmonicInterface.vnet"
            cmd0 = r"sed -e 's/endmodule/initial begin\n    $sdf_annotate(\"HarmonicInterface.sdf\", dut);\n        end\nendmodule/' < tb_HarmonicInterface.v > tb_HarmonicInterface.vnet"
            print os.system(cmd0)

        print runcmd
        return Cosimulation(
                runcmd,
                clk_in=clk_in,
                reset_in=reset_in,
                scl_in=scl_in,
                cs_in=cs_in,
                din=din,
                nco_i=nco_i,
                nco_q=nco_q,
                multA=multA,
                multB=multB,
                clk_out=clk_out,
                reset_out=reset_out,
                scl_out=scl_out,
                cs_out=cs_out,
                dout=dout,
                swAp=swAp,
                swAn=swAn,
                cintAn=cintAn,
                zeroAn=zeroAn,
                fastAn=fastAn,
                tuneAn=tuneAn,
                cintAp=cintAp,
                zeroAp=zeroAp,
                fastAp=fastAp,
                tuneAp=tuneAp,
                swBp=swBp,
                swBn=swBn,
                cintBn=cintBn,
                zeroBn=zeroBn,
                fastBn=fastBn,
                tuneBn=tuneBn,
                cintBp=cintBp,
                zeroBp=zeroBp,
                fastBp=fastBp,
                tuneBp=tuneBp)

                
    else:
        return  _HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
            nco_i, nco_q, multA, multB,
            clk_out, reset_out, scl_out, cs_out, dout,
            swAp, swAn,
            cintAn, zeroAn, fastAn, tuneAn,
            cintAp, zeroAp, fastAp, tuneAp,
            swBp, swBn,
            cintBn, zeroBn, fastBn, tuneBn,
            cintBp, zeroBp, fastBp, tuneBp)

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
        cintBp, zeroBp, fastBp, tuneBp, cosim=COSIM)

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
                #indata = intbv(0xdeadbeef0368)[N_DATA_BITS:]

                yield self.sysreset()

                yield tx(spi, indata)

                # shift out data
                yield start(spi)
                for i in downrange(N_DATA_BITS):
                    collector[i] = dout
                    yield sendBit(spi, 0)
                yield stop(spi)
                print bin(indata, 48)
                print bin(collector, 48)
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
                #indata = intbv(0xdeadbeef0368)[N_DATA_BITS:]
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
        tb = self.bench_spi_tune()
        sim = Simulation(tb)
        sim.run()
        del tb


    def make_bench_spi_nco(self, fcw):
        harmonic = HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
            # connect NCO to switches
            nco_i, nco_q, nco_i, nco_q,
            clk_out, reset_out, scl_out, cs_out, dout,
            swAp, swAn,
            cintAn, zeroAn, fastAn, tuneAn,
            cintAp, zeroAp, fastAp, tuneAp,
            swBp, swBn,
            cintBn, zeroBn, fastBn, tuneBn,
            cintBp, zeroBp, fastBp, tuneBp,
            cosim=COSIM)

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
            invec.rst = 0
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

            for i in range(2*int(fcw2period(fcw, 16))):
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
        for fcw in [2**14-1, 2**13-4, 2**12, 2**8] +  [-1]*3:
        #for fcw in [2**14-1, 2**13-4, 2**12, 2**8]:
        #for fcw in [2**8]:
            if fcw == -1:
                fcw = randrange(2**14)
            tb = self.make_bench_spi_nco(fcw)
            sim = Simulation(tb)
            sim.run()
            del tb



def mkSeriesHarmonic(
        clk_in, clk_out,
        reset_in, reset_out,
        scl_in, scl_out,
        cs_in, cs_out,
        din, dout):

    class Signals: pass
    sig = Signals()

    # internal harmonic lines and outputs
    sig.ncoI, sig.ncoQ = [Signal(intbv(0)[0]) for i in range(2)]

    sig.swAn = Signal(intbv(0)[7:])
    sig.swAp = Signal(intbv(0)[7:])
    sig.swBn = Signal(intbv(0)[7:])
    sig.swBp = Signal(intbv(0)[7:])

    sig.cintAn, sig.zeroAn, sig.fastAn = [Signal(intbv(0)[0]) for i in range(3)]
    sig.cintAp, sig.zeroAp, sig.fastAp = [Signal(intbv(0)[0]) for i in range(3)]
    sig.cintBn, sig.zeroBn, sig.fastBn = [Signal(intbv(0)[0]) for i in range(3)]
    sig.cintBp, sig.zeroBp, sig.fastBp = [Signal(intbv(0)[0]) for i in range(3)]

    sig.tuneAn = Signal(intbv(0)[12:])
    sig.tuneAp = Signal(intbv(0)[12:])
    sig.tuneBn = Signal(intbv(0)[12:])
    sig.tuneBp = Signal(intbv(0)[12:])

    harmonic = HarmonicInterface(
            clk_in, reset_in, scl_in, cs_in, din,
            sig.ncoI, sig.ncoQ, sig.ncoI, sig.ncoQ,
            clk_out, reset_out, scl_out, cs_out, dout,
            sig.swAp, sig.swAn,
            sig.cintAn, sig.zeroAn, sig.fastAn, sig.tuneAn,
            sig.cintAp, sig.zeroAp, sig.fastAp, sig.tuneAp,
            sig.swBp, sig.swBn,
            sig.cintBn, sig.zeroBn, sig.fastBn, sig.tuneBn,
            sig.cintBp, sig.zeroBp, sig.fastBp, sig.tuneBp,
            cosim=False) # only make ONE Cosimulator instance, top level
    return (harmonic, sig)


class TestMultipleHarmonics:
    @classmethod
    def setup_class(cls):
        cls.N_STAGES = 10

        clk = clk_in = Signal(intbv(0)[0])
        scl = scl_in = Signal(intbv(0)[0])
        cs = cs_in = Signal(intbv(0)[0])
        mosi = din = Signal(intbv(0)[0])

        cls.sysclk = Signal(bool(0))
        cls.reset = reset_in = Signal(intbv(0)[0])

        class SPI: pass
        spi = SPI()
        spi.clk = cls.sysclk
        spi.scl = scl
        spi.cs = cs
        spi.din = mosi
        cls.spi = spi

        cls.sysclock = cls.mksysclock()
        #cls.spiclock = cls.mkspiclock()

        #cls.stages = stages

    @classmethod
    def mksysclock(cls):
        @always(delay(PERIOD//2))
        def sysclock():
            cls.sysclk.next = not cls.sysclk
        return sysclock

    def mkstages(self):
        #create a series chain of harmonics
        clk_in = self.spi.clk
        scl_in = self.spi.scl
        cs_in = self.spi.cs
        din = self.spi.din
        reset_in = self.reset

        stages = []
        for i in range(self.N_STAGES):
            class Signals: pass
            sig = Signals()
            sig.clk_out = Signal(intbv(0)[0])
            sig.reset_out = Signal(intbv(0)[0])
            sig.scl_out = Signal(intbv(0)[0])
            sig.cs_out = Signal(intbv(0)[0])
            sig.dout = Signal(intbv(0)[0])


            harmonic, internal = mkSeriesHarmonic(
                    clk_in, sig.clk_out,
                    reset_in, sig.reset_out,
                    scl_in, sig.scl_out,
                    cs_in, sig.cs_out,
                    din, sig.dout)

            stages.append((harmonic, internal, sig))

            clk_in = sig.clk_out
            reset_in = sig.reset_out
            scl_in = sig.scl_out
            cs_in = sig.cs_out
            din = sig.dout
        return stages

    def sysreset(self):
        self.reset.next = 0
        yield self.sysclk.posedge
        self.reset.next = 1
        yield self.sysclk.posedge

    def bench_series_lines(self):
        stages = self.mkstages()
        @instance
        def check():
            for i in range(2**4):
                if DEBUG:
                    print '--------------------------------'
                    print 'iteration:', i
                i = intbv(i)

                #self.sysclock.next = 0
                yield self.sysreset()

                self.spi.clk.next = i[3]
                self.spi.scl.next = i[2]
                self.reset.next = i[1]
                self.spi.cs.next = i[0]
                yield self.sysclk.posedge
                yield delay(1000)

                for n in range(self.N_STAGES):
                    if DEBUG:
                        print
                        print 'stage:', n
                        print ''.join(map(bin, [
                            self.spi.clk,
                            self.spi.scl,
                            self.reset,
                            self.spi.cs]))
                        print ''.join(map(bin, [
                            stages[n][2].clk_out,
                            stages[n][2].scl_out,
                            stages[n][2].reset_out,
                            stages[n][2].cs_out]))
                    assert self.spi.clk == stages[n][2].clk_out
                    assert self.spi.scl == stages[n][2].scl_out
                    assert self.reset == stages[n][2].reset_out
                    assert self.spi.cs == stages[n][2].cs_out

            raise StopSimulation
        return self.sysclock, [s[0] for s in stages], check

    def test_series_lines(self):
        tb = self.bench_series_lines()
        sim = Simulation(tb)
        sim.run()


    def bench_spi_passthru(self):
        stages = self.mkstages()
        @instance
        def check():
            print '==========================='
            print 'spi_passthru'
            # a batch of random inputs
            for trial in range(10):
                collector = intbv(0)[N_DATA_BITS:]
                indata = intbv(randrange(2**N_DATA_BITS))[N_DATA_BITS:]
                #indata = intbv(0xdeadbeef0368)[N_DATA_BITS:]
                #indata = intbv(-1)[N_DATA_BITS:]
                print bin(indata)

                self.spi.scl.next = 0
                self.spi.cs.next = 1
                yield self.sysreset()
                print 'did reset'

                yield tx(self.spi, indata)
                print 'sent txdata0'

                #shift block to last instance
                for i in range(self.N_STAGES - 1):
                    yield tx(self.spi, intbv(0)[N_DATA_BITS:])
                    print 'txdata'

                #for n in range(self.N_STAGES):
                    #print bin(stages[n][2].dout)

                # shift out data
                yield start(self.spi)
                for i in downrange(N_DATA_BITS):
                    bit = collector[i] = stages[-1][2].dout
                    #print i, bin(bit)
                    yield sendBit(self.spi, 0)
                yield stop(self.spi)
                assert collector == indata
            raise StopSimulation
        #return self.sysclock, [s[0] for s in stages], check
        return self.sysclock, [s[0] for s in stages], check

    def test_spi_passthru(self):
        tb = self.bench_spi_passthru()
        sim = Simulation(tb)
        sim.run()


if __name__ == '__main__':
    TestSingleHarmonic().test_spi_shift()
    TestSingleHarmonic().test_spi_passthru()
    TestSingleHarmonic().test_spi_nco()

    #multiple = TestMultipleHarmonics()
    #multiple.setup_class()
    #multiple.test_series_lines()
    #multiple.test_spi_passthru()



