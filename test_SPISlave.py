import random

from myhdl import *

from SPISlave import SPISlave


PERIOD = 10
#N = 16*3

# SPI bus transaction helper
def start(spi):
    spi.cs.next = 0
    yield spi.clk.posedge

def sendBit(spi, b):
    spi.din.next = b
    yield spi.clk.posedge
    spi.scl.next = 1
    yield spi.clk.posedge
    spi.scl.next = 0
    yield spi.clk.posedge


def stop(spi):
    spi.cs.next = 1
    yield spi.clk.posedge

def tx(spi, word):
    yield start(spi)
    for i in downrange(len(word)):
        yield sendBit(spi, word[i])
    yield stop(spi)


class TestShiftRegister:
    def makeN_tester(self, N):
        clk = Signal(bool(0))
        reset, scl, cs = [Signal(bool(0)) for i in range(3)]
        din = Signal(intbv(0)[0])
        dout = Signal(intbv(0)[0])

        class SPI:
            pass
        spi = SPI()
        spi.clk = clk
        spi.scl = scl
        spi.cs = cs
        spi.din = din
        spi.dout = dout

        # dependent signals
        data = Signal(intbv(0)[N:])
        indata = Signal(intbv(0)[N:])

        spislave = SPISlave(
                N, reset, scl, cs, din,
                dout, data)


        # system clock generator
        @always(delay(PERIOD//2))
        def clkgen():
            clk.next = not clk

        # feed some random input words
        @instance
        def tester():
            collector = intbv(0)[N:]
            for iteration in range(10):
                indata.next = intbv(random.randrange(2**32))[N:]
                reset.next = 1
                yield clk.negedge
                yield tx(spi, indata)
                assert data == indata

                # shift out data
                yield start(spi)
                for i in downrange(N):
                    collector[i] = dout
                    yield sendBit(spi, 0)
                yield stop(spi)
                assert collector == indata

            raise StopSimulation

        return instances()

    def test_dataOut(self):
        for N in [2,4,8,16,32,48]:
            tb = self.makeN_tester(N)
            sim = Simulation(tb)
            sim.run()

    def bench_seriesDevices(self):
        clk = Signal(bool(0))
        reset, scl, cs = [Signal(bool(0)) for i in range(3)]
        din = Signal(intbv(0)[0])
        d0 = Signal(intbv(0)[0])
        d1 = Signal(intbv(0)[0])
        d2 = Signal(intbv(0)[0])
        dout = Signal(intbv(0)[0])

        class SPI:
            pass
        spi = SPI()
        spi.clk = clk
        spi.scl = scl
        spi.cs = cs
        spi.din = din
        spi.dout = dout

        N = 16
        N_SERIES = 4
        # intbv is 64bit max...
        assert (N*N_SERIES) <= 64

        # dependent signals
        data0 = Signal(intbv(0)[N:])
        data1 = Signal(intbv(0)[N:])
        data2 = Signal(intbv(0)[N:])
        data3 = Signal(intbv(0)[N:])

        spi0 = SPISlave(N, reset, scl, cs, din, d0, data0)
        spi1 = SPISlave(N, reset, scl, cs, d0, d1, data1)
        spi2 = SPISlave(N, reset, scl, cs, d1, d2, data2)
        spi3 = SPISlave(N, reset, scl, cs, d2, dout, data3)
        indata = Signal(intbv(0)[N_SERIES*N:])


        # system clock generator
        @always(delay(PERIOD//2))
        def clkgen():
            clk.next = not clk

        # feed some random input words
        @instance
        def tester():
            collector = intbv(0)[N_SERIES*N:]
            assert len(indata) == len(collector)
            for iteration in range(10):
                indata.next = random.randrange(2**64)
                reset.next = 1
                yield tx(spi, indata)

                # shift out data
                # sample dout BEFORE sending bit
                yield start(spi)
                for i in downrange(N_SERIES*N):
                    collector[i] = dout
                    yield sendBit(spi, 0)
                yield stop(spi)
                assert collector == indata
            raise StopSimulation

        return instances()

    def test_seriesDevices(self):
        tb = self.bench_seriesDevices()
        sim = Simulation(tb)
        sim.run()

    def vcd_test_timing(self):
        def bench_SPISlave():
            return self.makeN_tester(8)

        tb = traceSignals(bench_SPISlave)
        sim = Simulation(tb)
        sim.run()


if __name__ == '__main__':
    TestShiftRegister().vcd_test_timing()

