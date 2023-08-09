all: compile

VERILOG_SOURCES += hdl/Add.v

compile:
	verilator -Wno-fatal --trace --cc --exe --sv --timing --build ${VERILOG_SOURCES} sim_main.cpp  -CFLAGS "$(shell python3 -m pybind11 --includes)"  -LDFLAGS "-lpython3.8" 

run:
	export PYTHONPATH=$PYTHONPATH:/home/lx071/.local/lib/python3.8/site-packages && \
	cd obj_dir&&./VAdd&&cd ..
	
clean:
	-rm -rf verilator build obj_dir *.log *.dmp *.vpd core dump.vcd utils/__pycache__
