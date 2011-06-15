

modules=HarmonicInterface.py
#modules=$(shell ls *.py | grep -v '^test_')
verilog=$(modules:.py=.v)
tests=$(foreach mod, $(modules), test_$(mod:.py=.test))
vcd=$(foreach mod, $(modules), bench_$(mod:.py=.vcd))


all: test hdl
	@echo $(modules)

test: $(tests)

hdl: $(verilog)

install: $(verilog)
	scp $(verilog) dwhite@eel.unl.edu:sun-env/8rf/atoi_digital/RTL/

bench_%.vcd: test_%.py %.py
	python $<

test_%.test: test_%.py
	py.test --resultlog=$@ $<

%.v : %.py test_%.test
	python $<

clean:
	rm -f *.v
	rm -f *.vcd*
	rm -f *.pyc
	rm -f *.test
