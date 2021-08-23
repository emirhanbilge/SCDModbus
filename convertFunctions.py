def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def s16floatfactor(value,factor):
    temp = s16(value[0] | (value[1]<<8))
    temp = float(temp)*factor
    return round(temp,2)
    #round(temp,2)

def s32floatfactor(value,factor):
    temp = value[0] | (value[1]<<8) | (value[2]<<16) | (value[3]<<24)
    temp = float(temp)*factor
    return temp