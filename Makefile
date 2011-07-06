SHELL=/bin/bash

# Top-level modules
#   other files are support sub-modules
modules=HarmonicInterface.py Chain0Ctl.py

verilog=$(modules:.py=.v)
tests=$(foreach mod, $(modules), test_$(mod:.py=.test))
vcd=$(foreach mod, $(modules), bench_$(mod:.py=.vcd))

PYTHON=python
PY_TEST=pypy -m pytest

all: test hdl
	@echo $(modules)

test: $(tests)

hdl: $(verilog)

install: $(verilog)
	scp $(verilog) \
	    tb_HarmonicInterface.{v,vnet} \
	    dwhite@eel.unl.edu:sun-env/8rf/atoi_digital/RTL/


bench_%.vcd: test_%.py %.py
	$(PYTHON) $<

test_%.test: test_%.py %.py
	$(PY_TEST) --resultlog=$@ $<

%.v : %.py test_%.test
	$(PYTHON) $<

clean:
	rm -f *.v
	rm -f *.vcd*
	rm -f *.pyc
	rm -f *.test
