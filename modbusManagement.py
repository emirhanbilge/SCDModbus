import modbusServer as mdbs
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from convertFunctions  import s16floatfactor , s32floatfactor
from manageSCD import *


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
    binaryArr = []
    while(intNum):
        binaryArr.append(intNum %2 )
        intNum = intNum / 2 

    return binaryArr[::-1]

def convertDecimal(arr):
    lenght= len(arr)
    number = 0
    if lenght  <2 :
        return -1
    else:
        for i in range(lenght):
            number += arr[i] * 2**i
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
    for i in range(16-len(binVal)):
        settingsAll.append(0)
    for i in binVal:
        settingsAll(i)
    return settingsAll

def secondSettingBlock():
    settingsAll = []
    binVal = convertBinary(mdbs.readSettings2(a=(mdbs.Context,))[0])
    for i in range(16-len(binVal)):
        settingsAll.append(0)
    for i in binVal:
        settingsAll(i)
    return settingsAll

def closeCommand():
    binVal2 = convertBinary(mdbs.readSettings2(a=(mdbs.Context,))[0])
    binVal2[15] = 0
    writeSTESettingToModbusSettingsSecondAll(convertDecimal(binVal2))

async def controlValues():
    # Değerlerin sıralanışı MSB olarak söylenmiştir 1. bitten kasıt MSB'dir 
    # 1. bit sensör testi 
    # 2-3 . bit sensör hız ayarı 
    # 4.bit delete sensör data
    # 5-8 bit arası hata kodları için ayrılmıştır.
    # 9-14 bit arası Time için ayarlanmıştır
    # 15. bit Süreli ya da süresiz yayın için ayarlandı
    # 16. bit STE Result başlatma / durdurma için ayarlandı
    controlArr = firstSettingBlock()

    if controlArr[15] == 1:
        testResult = await selfTest()
        binVal = convertBinary(mdbs.readSettings1(a=(mdbs.Context,))[0])
        binVal[15] = 0 
        binVal[11] = 0 
        binVal[10] = 0
        binVal[10] = 0
        binVal[9] = testResult
        writeSTESettingToModbusSettingsFirstAll(convertDecimal(binVal))
        closeCommand()
        # Sensör Tesi Yapacak ve error kısmına varsa hata yazıcak

    elif controlArr[12] == 1:
        await deleteFlashMemory()
        binVal = convertBinary(mdbs.readSettings1(a=(mdbs.Context,))[0])
        binVal[12] = 0 
        writeSTESettingToModbusSettingsFirstAll(convertDecimal(binVal))
        closeCommand()

    elif controlArr[0] == 1:
        if convertDecimal(controlArr[13:15])<5:
            await setOutputDataRates(bytearray(convertDecimal(controlArr[13:15])))
            # SCD ye decimal değerin byte versiyonu yollanacak
        else:
           await setOutputDataRates(bytearray(b'\x00'))

        if controlArr[3] == 1: # Süresiz yayın demektir
            if not await ToggleStatu():
                await startToggle()
                await getSTEResultNotifyNoTime
            # Burada yayın başlatılır
        else:
            binVal = convertBinary(mdbs.readSettings1(a=(mdbs.Context,))[0])
            if convertDecimal(controlArr[2:7]):
                await getSTEResultNotifyWithTime(convertDecimal(controlArr[4:8]))
            else:
                await getSTEResultNotifyWithTime(5)
            binVal[3] = 0
            writeSTESettingToModbusSettingsFirstAll(convertDecimal(binVal))
            closeCommand()
    else:
        pass # yayın kapalı periyot çalıştırılır ya da herhangi bir şey yapmayabilir



async def mainLoopAPI():
    mainControlArr = secondSettingBlock()

    while(1):
        
        if mainControlArr[15]: # yönetim modbus tarafında olacak 0 olursa bizim tarafımıza geçecektir
            if mainControlArr[14]: # kayıt ile ilgili kısım
                if mainControlArr[13]:# periyodik olacak demektir 
                    helperSetting = firstSettingBlock()
                    if convertDecimal(mainControlArr[9:13]) and convertDecimal(helperSetting[4:8]): # Periyodik seçilip zaman 0000 yollandıysa eğer test periodic çalışacak
                        await testPeriodic()
                    else:# bu durumda zaman 0 değildir ve ayarlara bakılacak
                        valDelayTime = convertDecimal(mainControlArr[3:5])
                        delayTimeResult = 0
                        if valDelayTime == 0:
                            delayTimeResult = 3600 *24* convertDecimal(mainControlArr[9:13])
                        elif valDelayTime == 1:
                            delayTimeResult = 3600 * convertDecimal(mainControlArr[9:13])
                        else:
                            delayTimeResult = 60* convertDecimal(mainControlArr[9:13])
                        await periodicTime( bytearray(convertDecimal(helperSetting[4:8])) ,  bytearray(delayTimeResult) , bytearray(convertDecimal(mainControlArr[7:9])) )
                else:
                    if convertDecimal(mainControlArr[10:14]) and convertDecimal(mainControlArr[7:9]<5):# kayıt zamanı 0 yollamadıysa eğer
                        await saveDataInFlash( bytearray(convertDecimal(mainControlArr[7:9])     ,bytearray(convertDecimal(mainControlArr[9:13])  )))
                    else: # time olarak 0000 girdiyse zamana default 4 saniyelik kayıt alınacak
                        await saveDataInFlash( b'\x00'     ,bytearray(4)  )
                downloadVal = await getDataFlowStatus()
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
            time.sleep(1)
        



