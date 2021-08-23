import modbusServer as mdbs
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from convertFunctions  import s16floatfactor , s32floatfactor
import manageSCD as mng
import time


sendModBus = []
accelroVariance = []


def generate_mdbs_values(acceloreMeterVals , VarianceVals):
        if len(acceloreMeterVals)<23 and len(VarianceVals)<23 :
            builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Little)
            for i in acceloreMeterVals:
                builder.add_16bit_int(i)  
            for i in VarianceVals:
                builder.add_32bit_float(i)  
           
            payload = builder.to_registers() 
            mdbs.updating_custom_writer(a=(mdbs.Context,),values =payload)

def writeSTEResultModbus(data):
    liveResult = bytearray(data)
    #print(" RESULT Variance x : " , s32floatfactor(liveResult[6:10],0.01), " RESULT : accelero x" , s16floatfactor(liveResult[0:2],1))
    #print(" RESULT Variance y : " , s32floatfactor(liveResult[10:14],0.01), " RESULT : accelero y" , s16floatfactor(liveResult[2:4],1))
    #print(" RESULT Variance y : " , s32floatfactor(liveResult[14:18],0.01), " RESULT : accelero y" , s16floatfactor(liveResult[4:6],1))
    i1 = (int(s16floatfactor(liveResult[0:2],1000)))
    i2 = (int(s16floatfactor(liveResult[2:4],1000)))
    i3 = (int(s16floatfactor(liveResult[4:6],1000)))
    sendModBus.append(i1)
    sendModBus.append(i2)
    sendModBus.append(i3)
    i4 = s32floatfactor(liveResult[6:10],0.01)
    i5 = s32floatfactor(liveResult[10:14],0.01)
    i6 = s32floatfactor(liveResult[14:18],0.01)
    accelroVariance.append(i4)
    accelroVariance.append(i5)
    accelroVariance.append(i6)
    generate_mdbs_values(sendModBus , accelroVariance)

def convertBinary(intNum):
    print("********************" , intNum)
    binaryArr = []
    while(intNum):
        binaryArr.append(intNum %2 )
        intNum = int(intNum / 2) 
    return binaryArr

def convertDecimal(arr):
    lenght= len(arr)
    number = 0
    if lenght  <2 :
        return number
    else:
        for i in range(lenght):
            number += int(arr[i]) * 2**i
    return number

def writeSTESettingToModbusSettings1(data):
    writeModbusArr = []
    writeModbusArr.append(0)
    writeModbusArr.append(data[1])
    for i in range(8):
        writeModbusArr.append(0)
    writeModbusArr.append(data[0])
    builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Little)
    builder.add_16bit_int(convertDecimal(writeModbusArr))
    payload = builder.to_registers()
    mdbs.updating_settings1_writer(a=(mdbs.Context,),values =payload) 

def writeSTESettingToModbusSettingsFirstAll(data):
    builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Little)
    builder.add_16bit_int(convertDecimal(data))
    payload = builder.to_registers()
    mdbs.updating_settings1_writer(a=(mdbs.Context,),values =payload) 


def writeSTESettingToModbusSettingsSecondAll(data):
    builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Little)
    builder.add_16bit_int(convertDecimal(data))
    payload = builder.to_registers()
    mdbs.updating_settings2_writer(a=(mdbs.Context,),values =payload) 


def firstSettingBlock():
    settingsAll = []
    binVal = convertBinary(mdbs.readSettings1(a=(mdbs.Context,))[0])
    if len(binVal) :
        for i in binVal:
            settingsAll.append(i)
        for i in range(16-len(binVal)):
            settingsAll.append(0)
        return settingsAll
    return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
def secondSettingBlock():
    settingsAll = []
    binVal = convertBinary(mdbs.readSettings2(a=(mdbs.Context,))[0])
    if len(binVal) :
        for i in binVal:
            settingsAll.append(i)
        for i in range(16-len(binVal)):
            settingsAll.append(0)
        return settingsAll

    return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
def closeCommand():
    binVal2 = firstSettingBlock()
    binVal2[15] = 0
    writeSTESettingToModbusSettingsSecondAll(binVal2)

async def controlValues():
    print("Settings 1 Kısmında")
    # Değerlerin sıralanışı MSB olarak söylenmiştir 1. bitten kasıt MSB'dir 
    # 1. bit sensör testi 
    # 2-3 . bit sensör hız ayarı 
    # 4.bit delete sensör data
    # 5-8 bit arası hata kodları için ayrılmıştır.
    # 9-14 bit arası Time için ayarlanmıştır
    # 15. bit Süreli ya da süresiz yayın için ayarlandı
    # 16. bit STE Result başlatma / durdurma için ayarlandı
    controlArr = firstSettingBlock()
    print("Setting 1 " , controlArr)
    if controlArr[15] == 1:
        print("Sensör testinde")
        try:
            await mng.connect()
        except :
            print("Çoktan bağlı")
        testResult = await mng.selfTest()
        binVal = firstSettingBlock()
        binVal[15] = 0 
        binVal[11] = 0 
        binVal[10] = 0
        binVal[10] = 0
        if testResult == b'\xc0':
            
            binVal[9] = 0
        else:
            binVal[9] = 1
        await mng.disconnect()
        writeSTESettingToModbusSettingsFirstAll((binVal))
        closeCommand()
        # Sensör Tesi Yapacak ve error kısmına varsa hata yazıcak

    elif controlArr[12] == 1:
        print("Hafıza silmede")
        await mng.connect()
        await mng.deleteFlashMemory()
        await mng.disconnect()
        binVal = firstSettingBlock()
        binVal[12] = 0 
        writeSTESettingToModbusSettingsFirstAll(binVal)
        closeCommand()

    elif controlArr[2] == 1:
        print("Hız sensörü ayarlanıyor")
        if convertDecimal(controlArr[13:15])<5:
            await mng.connect()
            speed = controlArr[13:15]
            speedbyte = b'\x00'
            if speed[0]== 0 and speed[1] == 1:
                speedbyte = b'\x01'
            elif speed[0]== 1 and speed[1] == 0:
                speedbyte = b'\x02'
            elif speed[0]== 1 and speed[1] == 1:
                speedbyte = b'\x03'
            await mng.setOutputDataRates(speedbyte[0])
            await mng.disconnect()
            # SCD ye decimal değerin byte versiyonu yollanacak
        else:
            await mng.connect()
            await mng.setOutputDataRates(bytearray(b'\x00'))
            await mng.disconnect()

        if controlArr[2] == 1: # Süresiz yayın demektir
            print("Sürekli streamde")
            await mng.connect()
            if not await mng.ToggleStatu():
                await mng.startToggle()
                await mng.getSTEResultNotifyNoTime()
            await mng.disconnect()
            # Burada yayın başlatılır
        else:
            print("Süreli Streamde")
            binVal = firstSettingBlock()
            await mng.connect()
            if convertDecimal(controlArr[2:7]):
                await mng.getSTEResultNotifyWithTime(convertDecimal(controlArr[4:8]))
            else:
                await mng.getSTEResultNotifyWithTime(30)
            await mng.disconnect()
            binVal[3] = 0
            writeSTESettingToModbusSettingsFirstAll(binVal)
            closeCommand()
    else:
        pass # yayın kapalı periyot çalıştırılır ya da herhangi bir şey yapmayabilir



async def mainLoopAPI():
    mainControlArr = secondSettingBlock()
    writeSTESettingToModbusSettingsSecondAll([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    writeSTESettingToModbusSettingsFirstAll([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    while(1):
        
        mainControlArr = secondSettingBlock()
        print("Settings 2 bit dizisi " , mainControlArr , " 15. index " , mainControlArr[15] , " son arr " ,mainControlArr[0]) 
        if mainControlArr[15] ==1: # yönetim modbus tarafında olacak 0 olursa bizim tarafımıza geçecektir
            print("Modbus Yönetiminde")
            if mainControlArr[14] ==1: # kayıt ile ilgili kısım
                print("Kayıt alma kısmında")
                if mainControlArr[13] == 1:# periyodik olacak demektir
                    print("Periyodik alınacak")
                    helperSetting = firstSettingBlock()
                    if convertDecimal(mainControlArr[9:13]) and convertDecimal(helperSetting[4:8]): # Periyodik seçilip zaman 0000 yollandıysa eğer test periodic çalışacak
                        await mng.testPeriodic()
                    else:# bu durumda zaman 0 değildir ve ayarlara bakılacak
                        valDelayTime = convertDecimal(mainControlArr[3:5])
                        delayTimeResult = 0
                        if valDelayTime == 0:
                            delayTimeResult = 3600 *24* convertDecimal(mainControlArr[9:13])
                        elif valDelayTime == 1:
                            delayTimeResult = 3600 * convertDecimal(mainControlArr[9:13])
                        else:
                            delayTimeResult = 60* convertDecimal(mainControlArr[9:13])
                        #await periodicTime( bytearray(convertDecimal(helperSetting[4:8])) ,  bytearray(delayTimeResult) , bytearray(convertDecimal(mainControlArr[7:9])) )
                        await mng.periodicTime(b'\x00\x00',  b'\x00\x00' , b'\x00\x00' )
                else:
                    print(" kayıt alınıcak ama periyodik değil")
                    if convertDecimal(mainControlArr[10:14]) and convertDecimal(mainControlArr[7:9]<5):# kayıt zamanı 0 yollamadıysa eğer
                        await mng.connect()
                        await mng.saveDataInFlash( bytearray(convertDecimal(mainControlArr[7:9])     ,bytearray(convertDecimal(mainControlArr[9:13])  )))
                        await mng.disconnect()
                    else: # time olarak 0000 girdiyse zamana default 4 saniyelik kayıt alınacak
                        await mng.connect()
                        await mng.saveDataInFlash( b'\x00'     ,4  )
                        await mng.disconnect()
                await mng.connect()
                downloadVal = await mng.getDataFlowStatus()
                await mng.disconnect()
                if downloadVal == b'\x00':
                    mainControlArr[6] = 0
                    mainControlArr[5] = 0
                elif  downloadVal == b'\x01':
                    mainControlArr[6] = 0
                    mainControlArr[5] = 1
                elif  downloadVal == b'\x01':
                    mainControlArr[6] = 1
                    mainControlArr[5] = 0
                else:
                    mainControlArr[6] = 1
                    mainControlArr[5] = 1
                mainControlArr[15] = 0
                writeSTESettingToModbusSettingsSecondAll(mainControlArr)
            else:#kayıt yok setting 1 çalışır
                await controlValues()
        else:
            #print(mainControlArr)
            print("Burada")
            time.sleep(1)
        



