
import os

from myhdl import Cosimulation

cmd = "iverilog -o %s %s.v tb_%s.v" % (("HarmonicInterface",)*3)

