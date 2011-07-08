
from math import log, ceil
import os
from random import randrange

from myhdl import *

from Chain0Ctl import Chain0Ctl as _Chain0Ctl


CLKPERIOD = 10

N_DATA_BITS = 48
N_MUX_INPUTS = 49 #48 harmonics + CMI
N_MUX_BITS = int(ceil(log(N_MUX_INPUTS, 2)))


COSIM = os.getenv('MYHDL_COSIM')
if COSIM is None or COSIM == '0':
    COSIM = False
else:
    COSIM = True

SIMULATOR = os.getenv('MYHDL_SIMULATOR')
if COSIM and not SIMULATOR:
    SIMULATOR = 'iverilog'
    print 'INFO: using default cosimulator:', SIMULATOR

if COSIM:
    print '*** Cosimulation with %s ***' % SIMULATOR



def Chain0Ctl(
        reset, scl, cs, din,
        dout,
        txAn, txAp,
        txBn, txBp,
        swAn, swAp,
        swBn, swBp,
        fastAn, fastAp,
        fastBn, fastBp,
        tuneAn, tuneAp,
        tuneBn, tuneBp,
        cosim=COSIM):
    if cosim:
        if SIMULATOR == 'iverilog':
            runcmd = "vvp -m ./myhdl.vpi.%s -l Chain0Ctl.iverilog.log Chain0Ctl" % \
                    os.getenv('HOSTNAME')
            cmd0 = r"sed -e 's/endmodule/initial begin\n    $sdf_annotate(\"Chain0Ctl.sdf\", dut);\n        end\nendmodule/' < tb_Chain0Ctl.v > tb_Chain0Ctl.vnet"
            #cmd0 = "cp tb_Chain0Ctl.v tb_Chain0Ctl.vnet"
            cmd1 = "iverilog -gspecify -o Chain0Ctl \
                    ibm13rfrvt.verilog \
                    Chain0Ctl.vnet \
                    tb_Chain0Ctl.v"
                        
            print os.system(cmd0)
            print os.system(cmd1)

        elif SIMULATOR == 'cver':
                    #+sdf_annotate Chain0Ctl.sdf+tb_Chain0Ctl.dut \
            runcmd = "cver -l Chain0Ctl.cver.log +typdelays \
                    +loadvpi=./myhdl.cver.twain.so:vpi_compat_bootstrap \
                    +change_port_type \
                    -informs \
                    +printstats \
                    -v ibm13rfrvt.verilog \
                    Chain0Ctl.vnet \
                    tb_Chain0Ctl.v"
            cmd0 = r"sed -e 's/endmodule/initial begin\n    $sdf_annotate(\"Chain0Ctl.sdf\", dut);\n        end\nendmodule/' < tb_Chain0Ctl.v > tb_Chain0Ctl.vnet"
            print os.system(cmd0)
        elif SIMULATOR == 'verilog':
            runcmd = "verilog \
                    -l Chain0Ctl.vxl.log \
                    +loadvpi=./myhdl.verilog.doppler:myhdl_register \
                    -v ibm13rfrvt.verilog \
                    Chain0Ctl.vxl \
                    tb_Chain0Ctl.vnet"
            cmd0 = "echo \`timescale 1ns/1ps | cat - Chain0Ctl.vnet > Chain0Ctl.vxl"
            cmd1 = "echo \`timescale 1ns/1ps > tb_Chain0Ctl.vnet"
            cmd2 = r"sed -e 's/endmodule/initial begin  $sdf_annotate(\"Chain0Ctl.sdf\", dut); end  endmodule/' < tb_Chain0Ctl.v >> tb_Chain0Ctl.vnet"
            print os.system(cmd0)
            print os.system(cmd1)
            print os.system(cmd2)
        else:
            raise NameError('Unknown simulator: %s' % SIMULATOR)

        print runcmd
        return Cosimulation(
                runcmd,
                reset=reset,
                scl=scl,
                cs=cs,
                din=din,
                dout=dout,
                txAn=txAn,
                txAp=txAp,
                txBn=txBn,
                txBp=txBp,
                swAn=swAn,
                swAp=swAp,
                swBn=swBn,
                swBp=swBp,
                fastAn=fastAn,
                fastAp=fastAp,
                fastBn=fastBn,
                fastBp=fastBp,
                tuneAn=tuneAn,
                tuneAp=tuneAp,
                tuneBn=tuneBn,
                tuneBp=tuneBp
                )

    else:
        return  _Chain0Ctl(
               reset, scl, cs, din,
                dout,
                txAn, txAp,
                txBn, txBp,
                swAn, swAp,
                swBn, swBp,
                fastAn, fastAp,
                fastBn, fastBp,
                tuneAn, tuneAp,
                tuneBn, tuneBp
                )


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

