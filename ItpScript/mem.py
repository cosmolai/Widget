#-----------------------------------------------------
# mem.py
#-----------------------------------------------------
try:
    import itpii
    itp = itpii.baseaccess()
except:
    pass

def db(addr, length):
    return(itp.threads[0].memdump(itp.Address(addr), length, 1))

def dw(addr, length):
    return(itp.threads[0].memdump(itp.Address(addr), length/2, 2))

def dd(addr, length):
    return(itp.threads[0].memdump(itp.Address(addr), length/4, 4))

def eb(addr, value):
    return(itp.threads[0].mem(itp.Address(addr), 1, value))

def ew(addr, value):
    return(itp.threads[0].mem(itp.Address(addr), 2, value))

def ed(addr, value):
    return(itp.threads[0].mem(itp.Address(addr), 4, value))
