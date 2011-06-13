
from myhdl import *


from SwitchCtl import SwitchCtl


CLKPERIOD = 10


def runfor(steps):
    for i in range(steps):
        yield clk.posedge

def bench_SwitchCtl():

    clk, mult, se, cal = [Signal(bool(0)) for i in range(4)]
    sw = Signal(intbv(0)[7:])


    SwitchCtl_inst = SwitchCtl(mult, cal, se, sw)

    @always(delay(CLKPERIOD//2))
    def clkgen():
        clk.next = not clk

    @always(clk.posedge)
    def multgen():
        mult.next = not mult

    steps = 10
    @instance
    def stimulus():
        se.next = 0
        cal.next = 0
        for i in range(steps):
            yield clk.posedge

        se.next = 1
        for i in range(steps):
            yield clk.posedge

        cal.next = 1
        for i in range(steps):
            yield clk.posedge

        se.next = 0
        for i in range(steps):
            yield clk.posedge

        raise StopSimulation

    @instance
    def monitor():
        print 'c s m: a b c d e f g'
        print '-----:--------------'
        
        while True:
            yield clk.negedge
            print '%1d %1d %1d: %s' % \
                    (cal, se, mult, bin(sw, 7))

    return instances()


def test_bench_SwitchCtl():
    tracer = traceSignals(bench_SwitchCtl)
    sim = Simulation(tracer)
    sim.run()


def convert():
    toVerilog.header = '''
parmaeter True=1;
parameter False=0;
'''
    mult, cal, se = [Signal(bool(0)) for i in range(3)]
    sw = Signal(intbv(0)[7:])
    toVerilog(SwitchCtl, mult, cal, se, sw)

if __name__ == '__main__':
    convert()





