

modules=HarmonicInterface.py
#modules=$(shell ls *.py | grep -v '^test_')
verilog=$(modules:.py=.v)
tests=$(foreach mod, $(modules), test_$(mod))
vcd=$(foreach mod, $(modules), bench_$(mod:.py=.vcd))


all: test hdl
	@echo $(modules)

test: $(tests) $(vcd)

hdl: $(verilog)

install: $(verilog)
	scp $(verilog) dwhite@eel.unl.edu:sun-env/8rf/atoi_digital/RTL/

bench_%.vcd: test_%.py %.py
	python $<

%.v : %.py test_%.py
	python $<

clean:
	rm -f *.v
	rm -f *.vcd*
	rm -f *.pyc
