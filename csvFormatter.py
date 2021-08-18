def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def s16floatfactor(value,factor):
    temp = s16(value[0] | (value[1]<<8))
    temp = float(temp)*factor
    return round(temp,2)


def second(a , counter):
    f = open("result.txt","a")
    if counter % 56 == 1 :
        f.write((str(s16floatfactor(a[7:9],0.1))+ " " + str(s16floatfactor(a[9:11],0.1)) + " " + str(s16floatfactor(a[11:13],0.1))))
        f.write("\n")
        f.write((str(s16floatfactor(a[13:15],0.1))+ " " + str(s16floatfactor(a[15:17],0.1))+" "+ str(s16floatfactor(a[17:19],0.1))))
        f.write("\n")
        f.write((str(s16floatfactor(a[19:21],0.1)) + " "))
    elif counter == 56:
        f.write((str(s16floatfactor(a[5:7],0.1))+ " " + str(s16floatfactor(a[7:9],0.1)) +" " ))
        f.write("\n")
        
    elif counter % 56 != 1:
        
        if counter %3 == 2:
            f.write((str(s16floatfactor(a[5:7],0.1))+ " " + str(s16floatfactor(a[7:9],0.1)) +" " ))
            f.write("\n")
            f.write((str(s16floatfactor(a[9:11],0.1)) + " " + str(s16floatfactor(a[11:13],0.1)) + " " + str(s16floatfactor(a[13:15],0.1))))
            f.write("\n")
            f.write(str(str(s16floatfactor(a[15:17],0.1)) +" " +  str(s16floatfactor(a[17:19],0.1))  +" " + str(s16floatfactor(a[19:21],0.1))+" "))
            f.write("\n") 
        if counter %3 ==1 :
            f.write((" " + str(s16floatfactor(a[5:7],0.1)) + " "))
            f.write("\n")
            f.write((str(s16floatfactor(a[7:9],0.1)) + " " + str(s16floatfactor(a[9:11],0.1)) + " " + str(s16floatfactor(a[11:13],0.1) )))
            f.write("\n")
            f.write( (str(s16floatfactor(a[13:15],0.1)) +" " +  str(s16floatfactor(a[15:17],0.1))+" " +  str(s16floatfactor(a[17:19],0.1))))
            f.write("\n")
            f.write((str(s16floatfactor(a[19:21],0.1)) + " "))
        if counter % 3 == 0 :
            f.write( ( str(s16floatfactor(a[5:7],0.1))+" " + str(s16floatfactor(a[7:9],0.1))   +" "   +str(s16floatfactor(a[9:11],0.1)) ))
            f.write("\n")
            f.write( ( str(s16floatfactor(a[11:13],0.1)) + " " + str(s16floatfactor(a[13:15],0.1))+" " +(str(s16floatfactor(a[15:17],0.1)))))
            f.write("\n")
            f.write(str(s16floatfactor(a[17:19],0.1)) +" "+ str(s16floatfactor(a[19:21],0.1))+" ")
    f.close()


versionFlag = False
def first(a , counter):
    f = open("result.txt","a")
    if  counter % 56 == 1:
        if  not versionFlag:
            f.write((str(s16floatfactor(a[10:12],0.1))+ " " + str(s16floatfactor(a[12:14],0.1)) + " " + str(s16floatfactor(a[14:16],0.1))))
            f.write("\n")
            f.write((str(s16floatfactor(a[16:18],0.1))+ " " + str(s16floatfactor(a[18:20],0.1))))
        else:
            f.write(str( str(s16floatfactor(a[4:6],0.1)) + " " + str(s16floatfactor(a[6:8],0.1))    +" "+str(s16floatfactor(a[8:10],0.1))))
            f.write("\n")
            f.write((str(s16floatfactor(a[10:12],0.1))+ " " + str(s16floatfactor(a[12:14],0.1)) + " " + str(s16floatfactor(a[14:16],0.1))))
            f.write("\n")
            f.write(str(str(s16floatfactor(a[16:18],0.1))+ " " + str(s16floatfactor(a[18:20],0.1))))
    elif counter == 56:
        f.write(((str(s16floatfactor(a[4:6],0.1)))))
        f.write("\n")
    elif counter % 56 != 1:
        if counter %3 == 1:
            f.write((str(s16floatfactor(a[4:6],0.1))+ " " + str(s16floatfactor(a[6:8],0.1)) + " " + str(s16floatfactor(a[8:10],0.1))))
            f.write("\n")
            f.write((str(s16floatfactor(a[10:12],0.1)) + " " + str(s16floatfactor(a[12:14],0.1)) + " " + str(s16floatfactor(a[14:16],0.1))))
            f.write("\n")
            f.write((str(s16floatfactor(a[16:18],0.1))+" "+ str(s16floatfactor(a[18:20],0.1))))
        if counter %3 ==2 :
            f.write(  (" " + str(s16floatfactor(a[4:6],0.1))))
            f.write("\n")
            f.write( (str(s16floatfactor(a[6:8],0.1)) + " " + str(s16floatfactor(a[8:10],0.1)) + " " + str(s16floatfactor(a[10:12],0.1) )))
            f.write("\n")
            f.write( (str(s16floatfactor(a[12:14],0.1)) +" " +  str(s16floatfactor(a[14:16],0.1))+" " +  str(s16floatfactor(a[16:18],0.1))))
            f.write("\n")
            f.write(str(s16floatfactor(a[18:20],0.1)))
        if counter % 3 == 0 :
            f.write( (" " + str(s16floatfactor(a[4:6],0.1))+" " + str(s16floatfactor(a[6:8],0.1))))
            f.write("\n")
            f.write( (str(s16floatfactor(a[8:10],0.1)) + " " + str(s16floatfactor(a[10:12],0.1)) + " " + str(s16floatfactor(a[12:14],0.1))))
            f.write("\n")
            f.write( (str(s16floatfactor(a[14:16],0.1)) + " " + str(s16floatfactor(a[16:18],0.1)) + " " + str(s16floatfactor(a[18:20],0.1))))
            f.write("\n")
    f.close()

def getX_Y_Z(value):
    
    counter = 1
    flag = True
    for i in value:
        a =bytearray(i)
        try:
            if counter % 57== 0:
                flag = not flag
                versionFlag = True
                counter = 1
            if flag :
                first(a , counter)
            elif not flag:
                    
                if a[19] >225 :
                    a.append(255)
                else:
                    a.append(0)
                second(a , counter)
        except :
            print(a)
            print(len(a))
            print(counter)
            break
        counter +=1
