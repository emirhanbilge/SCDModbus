
def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def s16floatfactor(value,factor):
    temp = s16(value[0] | (value[1]<<8))
    temp = float(temp)*factor
    return round(temp,2)


first = open("14.35.13.17.8.2021.txt","r")
a1 = first.read().split("\n")

intArr = []
for i in a1:
    l = i.replace("[","").replace("]","").strip().split(",")
    m = []
    for j in l:
        #print(j)
        try:
            m.append(int(j))
        except:
            print("Err : " , i)
    intArr.append(m)

packetCounter = 0
ebbX = 0
c = 0
for i in intArr:

    indexS = 0
    indexF = 2
    
    if packetCounter > 4  30:
        print("Packet Counter : " , packetCounter)
        while(indexF<21):
            
            if ((s16floatfactor(i[indexS : indexF],0.1) > 3 or s16floatfactor(i[indexS : indexF],0.1) < -3)) and (indexS %2 == 0 ) and ebbX%2==0 :
                print("indexS : " , indexS , "  indexF  : " , indexF)
            if ( (s16floatfactor(i[indexS : indexF],0.1) > 3 or s16floatfactor(i[indexS : indexF],0.1) < -3)) and (indexS %2 == 1 ) and ebbX%2==1 :
                print("indexS : " , indexS , "  indexF  : " , indexF)
            
            indexS +=1
            indexF +=1
                                                                                                      
                                                                                                            
                                                                                                            
    packetCounter+=1
