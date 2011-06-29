
from myhdl import *


from BufferCtl import BufferCtl


CLKPERIOD = 10

# buffer register bits
# 15        cint/NotUsed
# 14        zero/tuneMode
# 13        se/buffer
# 12        fast
# [11:0]    tune


def test_muxCmp():
    """mode 00"""
    mode = Signal(intbv(0)[3:])
    sw = Signal(intbv(0)[4:])
    switch = BufferCtl(mode, sw)
    def test():
        a,b,c,d = downrange(4)
        @instance
        def inst():
            # mux comparitor
            mode.next = 0b00
            yield delay(10)
            assert sw[a] == 1
            assert sw[b] == 0
            assert sw[c] == 1
            assert sw[d] == 0
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()


def test_muxBuffer():
    """mode 01"""
    mode = Signal(intbv(0)[3:])
    sw = Signal(intbv(0)[4:])
    switch = BufferCtl(mode, sw)
    def test():
        a,b,c,d = downrange(4)
        @instance
        def inst():
            # mux buffer
            mode.next = 0b01
            yield delay(10)
            assert sw[a] == 1
            assert sw[b] == 0
            assert sw[c] == 0
            assert sw[d] == 1
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()



def test_tuneFast():
    """mode 10"""
    mode = Signal(intbv(0)[3:])
    sw = Signal(intbv(0)[4:])
    switch = BufferCtl(mode, sw)
    def test():
        a,b,c,d = downrange(4)
        @instance
        def inst():
            # fast vos tune
            mode.next = 0b10
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 1
            assert sw[c] == 1
            assert sw[d] == 0
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()


def test_tuneSlow():
    """mode 11"""
    mode = Signal(intbv(0)[3:])
    sw = Signal(intbv(0)[4:])
    switch = BufferCtl(mode, sw)
    def test():
        a,b,c,d = downrange(4)
        @instance
        def inst():
            # slow vos tune
            mode.next = 0b11
            yield delay(10)
            assert sw[a] == 0
            assert sw[b] == 1
            assert sw[c] == 0
            assert sw[d] == 1
            raise StopSimulation
        return instances()
    sim = Simulation(switch, test())
    sim.run()


