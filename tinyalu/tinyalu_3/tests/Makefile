# This is a Makefile

########################## Parameters #############################

# Object Verilog Files' catalog

ObjVFile = vfile.txt

# VCD File's name(.vcd)

VcdFile = test

# elf File's name(.out)

ElfFile = run

#####################################################################

# read Verilog Files' catalog

FileBuf := $(shell cat $(ObjVFile))


# make all

all: compile visual


# only make compile

compile:
	iverilog -o run.out $(FileBuf)

# only make visual ( make .elf file to the .vcd file )

visual:
	vvp -n $(ElfFile).out

# only open the wave

sim:
	gtkwave $(VcdFile).vcd

# clear middle files

clean:
	rm -rf *vcd *.out
