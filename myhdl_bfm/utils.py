from myhdl._compat import StringIO

def writeInst(f, intf):
    intf._inferInterface()
    intf.name = intf.func.__name__

    pm = StringIO()
    for portname in intf.argnames:
        print("    %s," % portname, file=pm)

    print(file=f)
    print("%s dut(" % intf.name, file=f)
    print(pm.getvalue()[:-2], file=f)
    print(");", file=f)
    print(file=f)


def merge(filename1, filename2, filename3):
    # open file in read mode and read all lines
    with open(filename1, "r") as f:
        lines = f.readlines()
    
    lines1 = lines[:-1]
    lines2 = [lines[-1]]

    # open file in read mode and read all lines
    with open(filename2, "r") as f:
        lines3 = f.readlines()

    # open file in write mode and write all lines
    with open(filename3, "w") as f:
        f.writelines(lines1 + lines3 + lines2)
    
