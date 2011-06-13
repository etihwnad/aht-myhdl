
from myhdl import *


from SwitchCtl import SwitchCtl


CLKPERIOD = 10



def test_diffMult():
    clk, mult, se, cal = [Signal(bool(0)) for i in range(4)]
    sw = Signal(intbv(0)[7:])
    switch = SwitchCtl(mult, cal, se, sw)
    def test():
        a,b,c,d,e,f,g = downrange(7)
        @instance
        def diffmult():
            # diff mode switch states
            cal.next = 0
            se.next = 0
            #+1
            mult.next = 0
            yield delay(10)
            assert sw[a] == 1
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 1
            assert sw[e] == 0
            assert sw[f] == 0
            assert sw[g] == 0
            #-1
            mult.next = 1
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 1
            assert sw[c] == 1
            assert sw[d] == 0
            assert sw[e] == 0
            assert sw[f] == 0
            assert sw[g] == 0
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()



def test_seMult():
    clk, mult, se, cal = [Signal(bool(0)) for i in range(4)]
    sw = Signal(intbv(0)[7:])
    switch = SwitchCtl(mult, cal, se, sw)
    def test():
        a,b,c,d,e,f,g = downrange(7)
        @instance
        def diffmult():
            # se mode switch states
            cal.next = 0
            se.next = 1
            #+1
            mult.next = 0
            yield delay(10)
            assert sw[a] == 1
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 0
            assert sw[f] == 0
            assert sw[g] == 1
            #-1
            mult.next = 1
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 1
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 0
            assert sw[f] == 0
            assert sw[g] == 1
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()



def test_diffCal():
    clk, mult, se, cal = [Signal(bool(0)) for i in range(4)]
    sw = Signal(intbv(0)[7:])
    switch = SwitchCtl(mult, cal, se, sw)
    def test():
        a,b,c,d,e,f,g = downrange(7)
        @instance
        def diffmult():
            # cal mode switch states
            cal.next = 1
            se.next = 0
            #+1
            mult.next = 0
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 1
            assert sw[f] == 1
            assert sw[g] == 0
            #-1
            mult.next = 1
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 1
            assert sw[f] == 1
            assert sw[g] == 0
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()




def test_seCal():
    clk, mult, se, cal = [Signal(bool(0)) for i in range(4)]
    sw = Signal(intbv(0)[7:])
    switch = SwitchCtl(mult, cal, se, sw)
    def test():
        a,b,c,d,e,f,g = downrange(7)
        @instance
        def diffmult():
            # cal mode switch states
            cal.next = 1
            se.next = 1
            #+1
            mult.next = 0
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 1
            assert sw[f] == 0
            assert sw[g] == 1
            #-1
            mult.next = 1
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 0
            assert sw[e] == 1
            assert sw[f] == 0
            assert sw[g] == 1
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
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
    #convert()
    #test_diffMult()
    pass





