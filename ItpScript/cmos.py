#-----------------------------------------------------
# cmos.py
#-----------------------------------------------------
try:
    import itpii
    itp = itpii.baseaccess()
except:
    pass

CMOS_INDEX = 0x74
CMOS_DATA  = 0x75
EXCMOS_INDEX = 0x76
EXCMOS_DATA  = 0x77

#-----------------------------------------------------
# cmos(start, length)
# show cmos registers from 0x00 to 0x7F
#
#   start:  start address of cmos register
#   length: length of register range to dump
#-----------------------------------------------------
def cmos(start, length):
    for i in range(length):
        itp.threads[0].port(CMOS_INDEX, start+i)
        itpii.printf("%02X: %02X\n", start+i, itp.threads[0].port(CMOS_DATA))
    return

#-----------------------------------------------------
# cmosall
# show cmos registers from 0x00 to 0x7F
#-----------------------------------------------------
def cmosall():
    itpii.printf("      00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \n")
    itpii.printf("+---+------------------------------------------------+\n")
    for i in range(0, 8, 1):
        itpii.printf(" %02X |", i*16)
        for j in range(0, 16, 1):
            itp.threads[0].port(CMOS_INDEX, i*16+j)
            itpii.printf(" %02X", itp.threads[0].port(CMOS_DATA))
        itpii.printf("\n")
    return

#-----------------------------------------------------
# excmos(start, length)
# show excmos registers from 0x00 to 0x7F
#
#   start:  start address of excmos register
#   length: length of register range to dump
#-----------------------------------------------------
def excmos(start, length):
    for i in range(length):
        itp.threads[0].port(EXCMOS_INDEX, start+i)
        itpii.printf("%02X: %02X\n", start+i, itp.threads[0].port(EXCMOS_DATA))
    return

#-----------------------------------------------------
# excmosall
# show excmos registers from 0x00 to 0x7F
#-----------------------------------------------------
def excmosall():
    itpii.printf("      00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F \n")
    itpii.printf("+---+------------------------------------------------+\n")
    for i in range(0, 8, 1):
        itpii.printf(" %02X |", i*16)
        for j in range(0, 16, 1):
            itp.threads[0].port(EXCMOS_INDEX, i*16+j)
            itpii.printf(" %02X", itp.threads[0].port(EXCMOS_DATA))
        itpii.printf("\n")
    return

#-----------------------------------------------------
# cmoswb(reg, value)
# write byte to cmos register with value
#
#   reg:    address of cmos register
#   value:  value to cmos register
#-----------------------------------------------------
def cmoswb(reg, value):
    itp.threads[0].port(CMOS_INDEX, reg)
    itp.threads[0].port(CMOS_DATA, value)
    return

#-----------------------------------------------------
# cmosww(reg, value)
# write word to cmos register with value
#
#   reg:    address of cmos register
#   value:  value to cmos register
#-----------------------------------------------------
def cmosww(reg, value):
    cmoswb(reg, value & 0xFF)
    cmoswb(reg+1, (value >> 8) & 0xFF)
    return

#-----------------------------------------------------
# cmoswd(reg, value)
# write dword to cmos register with value
#
#   reg:    address of cmos register
#   value:  value to cmos register
#-----------------------------------------------------
def cmoswd(reg, value):
    cmoswb(reg, value & 0xFF)
    cmoswb(reg+1, (value >> 8) & 0xFF)
    cmoswb(reg+2, (value >> 16) & 0xFF)
    cmoswb(reg+3, (value >> 24) & 0xFF)
    return
