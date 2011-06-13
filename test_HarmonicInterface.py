
import os
from myhdl import *

from HarmonicInterface import HarmonicInterface

#COSIM = True
COSIM = False

if COSIM:
    def HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp):
        cmd = "iverilog -o HarmonicInterface -gspecify \
                HarmonicInterface.vnet \
                ibm13rfrvt.v \
                tb_HarmonicInterface.v"
        os.system(cmd)

        return Cosimulation("vvp -m ./myhdl.vpi HarmonicInterface -sdf-verbose",
            clk_in = clk_in,
            reset_in = reset_in,
            scl_in = scl_in,
            cs_in = cs_in,
            din = din,
            nco_i = nco_i,
            nco_q = nco_q,
            multA = multA,
            multB = multB,
            clk_out = clk_out,
            reset_out = reset_out,
            scl_out = scl_out,
            cs_out = cs_out,
            dout = dout,
            swAp = swAp,
            swAn = swAn,
            cintAn = cintAn,
            zeroAn = zeroAn,
            fastAn = fastAn,
            tuneAn = tuneAn,
            cintAp = cintAp,
            zeroAp = zeroAp,
            fastAp = fastAp,
            tuneAp = tuneAp,
            swBp = swBp,
            swBn = swBn,
            cintBn = cintBn,
            zeroBn = zeroBn,
            fastBn = fastBn,
            tuneBn = tuneBn,
            cintBp = cintBp,
            zeroBp = zeroBp,
            fastBp = fastBp,
            tuneBp = tuneBp )

PERIOD = 100


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


# Sent to analog side
#swA.driven = 'reg'
#swB.driven = 'reg'
#cintA.driven = 'reg'
#cintB.driven = 'reg'
#zeroA.driven = 'reg'
#zeroB.driven = 'reg'
#fastA.driven = 'reg'
#fastB.driven = 'reg'
#tuneA.driven = 'reg'
#tuneB.driven = 'reg'


# test vector to send in via SPI
indata = Signal(intbv(0)[3*16:])

def start():
    scl_in.next = 0
    cs_in.next = 0
    yield clk_in.negedge

def sendBit(b):
    scl_in.next = 0
    din.next = b
    yield delay(2)
    scl_in.next = 1
    yield clk_in.negedge

def stop():
    scl_in.next = 0
    cs_in.next = 1
    yield clk_in.negedge

def spi_tx(word, n):
    yield start()
    for i in downrange(n):
        yield sendBit(word[i])
    yield stop()


def bench_HarmonicInterface():
    harmonic = HarmonicInterface(clk_in, reset_in, scl_in, cs_in, din,
        nco_i, nco_q, multA, multB,
        clk_out, reset_out, scl_out, cs_out, dout,
        swAp, swAn,
        cintAn, zeroAn, fastAn, tuneAn,
        cintAp, zeroAp, fastAp, tuneAp,
        swBp, swBn,
        cintBn, zeroBn, fastBn, tuneBn,
        cintBp, zeroBp, fastBp, tuneBp)

    @always_comb
    def wires():
        """Connect NCO to multiplier"""
        multA.next = nco_i
        multB.next = nco_q

    @always(delay(PERIOD//2))
    def clkgen():
        clk_in.next = not clk_in

    #@always(clk_in.posedge)
    #def spiclkgen():
        #scl_in.next = not scl_in

    @instance
    def transaction():
        reset_in.next = 1
        yield clk_in.negedge

        reset_in.next = 0
        yield clk_in.negedge

        reset_in.next = 1
        yield clk_in.negedge

        #                               /  channel A   \/  channel B   \
        #               cr/   fcw      \czsf/ tuneA    \czsf/ tuneA    \
        indata.next = 0b010101000000000010101000100000000101100001111111
        yield spi_tx(indata, 48)

        cs_in.next = 0
        for i in range(1000):
            yield clk_in.negedge

        #                               /  channel A   \/  channel B   \
        #               cr/   fcw      \czsf/ tuneA    \czsf/ tuneA    \
        indata.next = 0b010001011000100100001010100000001110100010111111
        yield spi_tx(indata, 48)
        #yield spi_tx(indata, 48)
        for i in range(1000):
            yield clk_in.negedge

        for i in range(10):
            yield clk_in.negedge

        raise StopSimulation

    return instances()





def test_bench_HarmonicInterface():
    tracer = traceSignals(bench_HarmonicInterface)
    sim = Simulation(tracer)
    sim.run()


if __name__ == '__main__':
    test_bench_HarmonicInterface()


