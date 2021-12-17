#-----------------------------------------------------
# mmpci.py
#-----------------------------------------------------
try:
    import itpii
    itp = itpii.baseaccess()
except:
    pass

PCIE_BASE = 0xE0000000

def cfg(bus, device, function):
    return(itp.threads[0].memdump(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12)), 0x40, 4))

def cfgbr(bus, device, function, offset):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 1))

def cfgbw(bus, device, function, offset, value):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 1, value))

def cfgwr(bus, device, function, offset):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 2))

def cfgww(bus, device, function, offset, value):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 2, value))

def cfgdr(bus, device, function, offset):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 4))

def cfgdw(bus, device, function, offset, value):
    return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 4, value))

def cfgb(*argvector):
    bus = int()
    device = int()
    function = int()
    offset = int()
    value = int()
    if len(argvector) < 4 or len(argvector) > 5:
        itpii.printf("Usage: cfgb(bus, device, function, offset, [value])\n")
        itpii.printf("ex:    cfgb(0, 31, 0, 0x04)\n")
        itpii.printf("ex:    cfgb(0, 31, 0, 0x04, 0x07)\n")
        return
    bus = argvector[0x0]
    device = argvector[0x1]
    function = argvector[0x2]
    offset = argvector[0x3]
    if len(argvector) == 4:
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 1))
    else:
        value = argvector[0x4]
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 1, value))

def cfgw(*argvector):
    bus = int()
    device = int()
    function = int()
    offset = int()
    value = int()
    if len(argvector) < 4 or len(argvector) > 5:
        itpii.printf("Usage: cfgw(bus, device, function, offset, [value])\n")
        itpii.printf("ex:    cfgw(0, 31, 0, 0x04)\n")
        itpii.printf("ex:    cfgw(0, 31, 0, 0x04, 0x0007)\n")
        return
    bus = argvector[0x0]
    device = argvector[0x1]
    function = argvector[0x2]
    offset = argvector[0x3]
    if len(argvector) == 4:
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 2))
    else:
        value = argvector[0x4]
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 2, value))

def cfgd(*argvector):
    bus = int()
    device = int()
    function = int()
    offset = int()
    value = int()
    if len(argvector) < 4 or len(argvector) > 5:
        itpii.printf("Usage: cfgd(bus, device, function, offset, [value])\n")
        itpii.printf("ex:    cfgd(0, 31, 0, 0x04)\n")
        itpii.printf("ex:    cfgd(0, 31, 0, 0x04, 0x000007)\n")
        return
    bus = argvector[0x0]
    device = argvector[0x1]
    function = argvector[0x2]
    offset = argvector[0x3]
    if len(argvector) == 4:
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 4))
    else:
        value = argvector[0x4]
        return(itp.threads[0].mem(itp.Address(PCIE_BASE + (bus << 20) + (device << 15) + (function << 12) + offset), 4, value))

