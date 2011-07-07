
from math import log, ceil
from random import randrange

from myhdl import *

from Chain0Ctl import Chain0Ctl


CLKPERIOD = 10

# buffer register bits
# 15        cint/NotUsed
# 14        zero/tuneMode
# 13        se/buffer
# 12        fast
# [11:0]    tune

N_DATA_BITS = 48
N_MUX_INPUTS = 49 #48 harmonics + CMI
N_MUX_BITS = int(ceil(log(N_MUX_INPUTS, 2)))

class TestChain0Ctl:
    #@classmethod
    def setup_method(self, method):
        #sham global clock
        self.mclk = Signal(bool(0))

        self.reset = Signal(intbv(0)[0])
        self.scl = Signal(intbv(0)[0])
        self.cs = Signal(intbv(0)[0])
        self.din = Signal(intbv(0)[0])
        self.dout = Signal(intbv(0)[0])

        self.txAn = Signal(intbv(0)[N_MUX_INPUTS:])
        self.txAp = Signal(intbv(0)[N_MUX_INPUTS:])
        self.txBn = Signal(intbv(0)[N_MUX_INPUTS:])
        self.txBp = Signal(intbv(0)[N_MUX_INPUTS:])

        self.swAn = Signal(intbv(0)[4:])
        self.swAp = Signal(intbv(0)[4:])
        self.swBn = Signal(intbv(0)[4:])
        self.swBp = Signal(intbv(0)[4:])

        self.fastAn = Signal(intbv(0)[0])
        self.fastAp = Signal(intbv(0)[0])
        self.fastBn = Signal(intbv(0)[0])
        self.fastBp = Signal(intbv(0)[0])

        self.tuneAn = Signal(intbv(0)[12:])
        self.tuneAp = Signal(intbv(0)[12:])
        self.tuneBn = Signal(intbv(0)[12:])
        self.tuneBp = Signal(intbv(0)[12:])

        self.ctl_inst = Chain0Ctl(
                self.reset, self.scl, self.cs, self.din,
                self.dout,
                self.txAn, self.txAp,
                self.txBn, self.txBp,
                self.swAn, self.swAp,
                self.swBn, self.swBp,
                self.fastAn, self.fastAp,
                self.fastBn, self.fastBp,
                self.tuneAn, self.tuneAp,
                self.tuneBn, self.tuneBp
                )

        @always(delay(CLKPERIOD//2))
        def mclockgen():
            self.mclk.next = not self.mclk
        self.mclkgen = mclockgen

    def teardown_method(self, method):
        pass

    def sysReset(self):
        self.reset.next = 0
        yield self.mclk.posedge
        self.reset.next = 1
        yield self.mclk.posedge
        #self.cs.next = 0
        #yield self.mclk.posedge
        #self.cs.next = 1
        #yield self.mclk.posedge

    def spiStart(self):
        self.cs.next = 0
        yield self.mclk.posedge

    def spiStop(self):
        self.scl.next = 0
        yield self.mclk.posedge
        self.cs.next = 1
        yield self.mclk.posedge

    def spiSendBit(self, b):
        self.scl.next = 0
        self.din.next = b
        yield self.mclk.posedge
        self.scl.next = 1
        yield self.mclk.posedge

    def spiTx(self, data):
        assert (len(data) % 16) == 0
        print 'data len:', len(data)
        print 'send: ', bin(data, 48)
        yield self.spiStart()
        for i in downrange(len(data)):
            yield self.spiSendBit(data[i])
        yield self.spiStop()


    def test_spi_shift(self):
        def test():
            @instance
            def inst():
                # a batch of random inputs
                for trial in range(10):
                    print '**** Trial', trial
                    collector = intbv(0)[N_DATA_BITS:]
                    indata = intbv(randrange(2**N_DATA_BITS))[N_DATA_BITS:]
                    #indata = intbv(0xdeadbeef0368)[N_DATA_BITS:]

                    print '*** sysReset'
                    yield self.sysReset()

                    print '*** spiTx: ', bin(indata, N_DATA_BITS)
                    yield self.spiTx(indata)

                    print '*** shift data out'
                    # shift out data
                    yield self.spiStart()
                    for i in downrange(N_DATA_BITS):
                        yield self.spiSendBit(0)
                        #sample data when scl==1
                        collector[i] = self.dout
                    print '*** spiStop'
                    yield self.spiStop()
                    print bin(indata, 48)
                    print bin(collector, 48)
                    assert collector == indata
                raise StopSimulation
            return inst, self.ctl_inst, self.mclkgen

        sim = Simulation(test())
        sim.run()


    def test_oneHot(self):
        """Only one output selected"""
        unusedA = Signal(intbv(0)[2:])
        muxSelA = Signal(intbv(0)[6:])
        unusedB = Signal(intbv(0)[2:])
        muxSelB = Signal(intbv(0)[6:])

        word2 = ConcatSignal(unusedA, muxSelA, unusedB, muxSelB)
        word1 = Signal(intbv(0)[16:])
        word0 = Signal(intbv(0)[16:])
        
        data = ConcatSignal(word2, word1, word0)

        expected = Signal(intbv(0)[N_MUX_INPUTS:])
        default = intbv(0)[N_MUX_INPUTS:]

        def test():
            @instance
            def inst():
                yield self.sysReset()

                # Mux A select lines
                for i in range(N_MUX_INPUTS):
                    muxSelA.next = i
                    word1.next = randrange(2**16)
                    word0.next = randrange(2**16)
                    expected.next = intbv(1 << i)[N_MUX_INPUTS:]
                    yield self.spiTx(data)
                    assert intbv(self.txAn.val, max=2**N_MUX_BITS) == expected
                    assert intbv(self.txAp.val, max=2**N_MUX_BITS) == ~expected

                # Mux A default none selected
                for i in range(N_MUX_INPUTS, 2**N_MUX_BITS):
                    muxSelA.next = i
                    yield self.spiTx(data)
                    assert intbv(self.txAn.val, max=2**N_MUX_BITS) == default
                    assert intbv(self.txAp.val, max=2**N_MUX_BITS) == ~default
                    
                # Mux B select lines
                for i in range(N_MUX_INPUTS):
                    muxSelB.next = i
                    expected.next = intbv(1 << i)[N_MUX_INPUTS:]
                    yield self.spiTx(data)
                    assert intbv(self.txBn.val, max=2**N_MUX_BITS) == expected
                    assert intbv(self.txBp.val, max=2**N_MUX_BITS) == ~expected

                # Mux B default none selected
                for i in range(N_MUX_INPUTS, 2**N_MUX_BITS):
                    muxSelB.next = i
                    yield self.spiTx(data)
                    assert intbv(self.txBn.val, max=2**N_MUX_BITS) == default
                    assert intbv(self.txBp.val, max=2**N_MUX_BITS) == ~default

                raise StopSimulation

            return inst, self.ctl_inst, self.mclkgen

        sim = Simulation(test())
        sim.run()


if __name__ == '__main__':
    tb = TestChain0Ctl()
    tb.setup_method('foo')
    tb.test_spi_shift()

