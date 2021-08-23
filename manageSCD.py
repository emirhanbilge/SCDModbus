import asyncio , datetime
from logging import error
from bleak import BleakScanner , BleakClient
import time , datetime , sys
import nest_asyncio
nest_asyncio.apply()
sys.path.append('../')
from scdCharacteristic import ServiceBulkDataTransfer,ServiceShortTermExperiment  ,ServiceSCDSettings
import modbusServer as mdbs
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from convertFunctions import s16floatfactor , s32floatfactor 
from modbusManagement import sendModBus , accelroVariance , writeSTEResultModbus ,secondSettingBlock , writeSTESettingToModbusSettingsFirstAll , writeSTESettingToModbusSettingsSecondAll
 


            

def setStartValuesModbus():
    writeSTESettingToModbusSettingsFirstAll(0)
    writeSTESettingToModbusSettingsSecondAll(0)



################################################################################################################ FOR NOTIFY ###############################################################################
allNotifiy = []
flagStartStop =[]
hundredPercent = 0
def notification_handler(sender, data):
   
    lists = []
    for i in data:
        lists.append(i)
    allNotifiy.append(lists)
    if len(allNotifiy) !=0:
        hundredPercent = int((len(allNotifiy) / int.from_bytes(bytearray(allNotifiy[0])[4:8] , "little"))*100) 
    if hundredPercent%10 == 0 :
        print("Yüzde %",hundredPercent," indirildi")
    #print(lists)
    if len(allNotifiy) ==  int.from_bytes(bytearray(allNotifiy[0])[4:8],"little"):
        print("************** " ,len(allNotifiy) ," Total Counter   Sağdaki paket sayısı" ,int.from_bytes(bytearray(allNotifiy[0])[4:8] , "little") )
        print("Download is successfully")


def notificationHandlerResult(sender, data):
    writeSTEResultModbus(data)


    
##########################################################################    DATA SAVE    ##############################################################


def writeDownload():
    now = datetime.datetime.now()
    nowFileName = str(now.hour) +"."+str(now.minute)+"."+str(now.second)+"."+str(now.day)+"."+str(now.month)+"."+str(now.year)+".txt"
    fo = open(nowFileName,"a")
    #getX_Y_Z(allNotifiy)
    for i in allNotifiy:
        for j in i:
            fo.write(str(j))
            fo.write(" ")
        fo.write("\n")
    fo.close()

########################################################################################################################################################


################################################################          MODE SELECTION         ###############################################
#Burada 0 olursa STE yani Short Time Experiment aktif olurken 255'te ise default value olarak gelir
# Mode selection sadece STE durmuşsa değiştirilmelidir. Başka bir work mode'a girmeden önce , yeni moda girdiğimiz 
# anda bu değer değiştirilmelidir. İki modumuz varsa 0. Modda isek 255'e girebilmek için 255 yaparız ve 255'e girer girmez 0 yaparız. vb
async def setModeSelection(mode):  #mode 0 : 0 değeri ; 1 ise 255 değerini yazar.
    print("First Mode Selection value")
    print(await getModeSelection())
    #1 byte'tır ve 0 ile 255 değeri alır. Bunun dışındaki değerler reserved değerlerdir.  
    if mode:
        await client.write_gatt_char(ServiceSCDSettings["ModeSelection"] , b"\x00")
        return await getModeSelection()
    else:
        await client.write_gatt_char(ServiceSCDSettings["ModeSelection"] , b"\xff")
        return await getModeSelection()
async def getModeSelection():
     return await client.read_gatt_char(ServiceSCDSettings["ModeSelection"])


async def selfTest():
    return await client.read_gatt_char(ServiceSCDSettings["SelfTestResult"])
    
#####################################################################################################################################


########################################       SCD  GENERIC COMMAND      ##############################
# 1 bytelık bir alandır 0x00 default değeri olup buraya komut geldikten sonra değerini 0x00'e döndürür yani 0x20 yollasak da daha 
# sonra burası 0x00 olur
# 0x10 Bu FOTA için kullanılır
# 0x20 Toggle Açıp Kapama için kullanılır burada değerler önemlidir.Eğer rolling counter (STE Resulttaki ) 0x20'de akış başlarsa 
# doğrudan 1 olur eğer 0 ise streaming yok demektir.
# 0x21 cmdResetThresholdFlags STE modunda tüm flagleri sıfırlama için kullanılır.
# 0x30 Flash datasını siler 9 saniye beklemek gerekebilir
async def getSCDgenericCommannds():
    return await client.read_gatt_char(ServiceSCDSettings["SCDGenericCommands"])

async def startToggle():
    vr = await getSTEResultRead()
    if (vr)[32] == 0:
        await client.write_gatt_char(ServiceSCDSettings["SCDGenericCommands"], b'\x20')

async def stopToggle():
    vr = await getSTEResultRead()
    if (vr)[32] != 0:
        await client.write_gatt_char(ServiceSCDSettings["SCDGenericCommands"], b'\x20')

async def ToggleStatu():
    vr = await getSTEResultRead()
    if (vr)[32] != 0:
        return 1
    return 0

async def deleteFlashMemory():
    #print("First SCD Generic Command Erase Flash Value")
    #print(await getSCDgenericCommannds())
    await client.write_gatt_char(ServiceSCDSettings["SCDGenericCommands"] ,b"\x30" )
   
async def resetSCD():
    #print("First SCD Generic Command Erase Flash Value")
    #print(await getSCDgenericCommannds())
    await client.write_gatt_char(ServiceSCDSettings["SCDGenericCommands"] ,b"\x21" )
   
###################################################################################################



########################################       Short Term Experiment / STE Conf Parameters and STE Results     ##############################

#Stream akışındaki sensörlerin hangileri aktif olacak onu belirler
# Default olarak hepsi kapalı gelmektedir. 0 disable 1 enabledir
# 0x01  enable acceleromenet
# 0x02 enableMagnetometer
# 0x04 enableLightSensor
# 0x08 enableTemperature sensor 
# tamamını kapamak istersek de 0xF0 ile kapayabiliriz

async def getAllSTEConfig():
    return await client.read_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"])

async def getSensorEnable():
    return (await client.read_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"]))[4]

async def getOutputDataRates():
    return (await client.read_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"]))[5]
async def getSensorRawValueToFlash():
    return (await client.read_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"]))[30]

async def getRollingCounter():
    return (await client.read_gatt_char(ServiceShortTermExperiment["STEResults"]))[32]

async def getSTEResultRead():
    return await client.read_gatt_char(ServiceShortTermExperiment["STEResults"])

async def getSTEResultNotify():

    global sendModBus
    global accelroVariance
    counterRasultTime = 0
    await client.start_notify(ServiceShortTermExperiment["STEResults"], notificationHandlerResult)
    while(counterRasultTime<10):
        try:
            await asyncio.sleep(1.0)
            accelroVariance = []
            sendModBus = []
        except:
            print("Error 1")
        counterRasultTime +=1
    await client.stop_notify(ServiceShortTermExperiment["STEResults"])
    #writeDownload()

async def getSTEResultNotifyWithTime(timeData):
    global sendModBus
    global accelroVariance
    counterRasultTime = 0
    await client.start_notify(ServiceShortTermExperiment["STEResults"], notificationHandlerResult)
    while(counterRasultTime<timeData):
        try:
            await asyncio.sleep(1.0)
            accelroVariance = []
            sendModBus = []
        except:
            print("Error 1")
        counterRasultTime +=1
    await client.stop_notify(ServiceShortTermExperiment["STEResults"])
    #writeDownload()


async def getSTEResultNotifyNoTime():
    global sendModBus
    global accelroVariance
    counterRasultTime = 0
    await client.start_notify(ServiceShortTermExperiment["STEResults"], notificationHandlerResult)
    mainControlArr = secondSettingBlock()
    while(mainControlArr[15]):
        try:
            mainControlArr = secondSettingBlock()
            await asyncio.sleep(1.0)
            accelroVariance = []
            sendModBus = []
        except:
            print("Error 1")
        counterRasultTime +=1
    await client.stop_notify(ServiceShortTermExperiment["STEResults"])

async def setSensorsEnables(byteArray):
    print("First Enable Sensor Value")
    default = bytearray(await getAllSTEConfig())
    print(default[4])
    arr= bytearray(default)
    arr[4] = byteArray[0]
    await client.write_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"],arr) 
    print("setSensorEnable Function setted Sensor Value")
    sensorsEn = await getSensorEnable()
    print(sensorsEn)
    


# low nible'da accelometer için ayarlar high nible'da ise light sensoru için değerlerler girilmelidir
# 0x?0 400Hz (default değeri)
# 0x?1 800Hz
# 0x?2 1.6kH
# 0x?3 3.2 kH
# 0x?4 6.4 kH
#bu değerler accolemeter içindi 

# light sensor için
# 0x0? 10Hz
# 0x1? 1.25Hz

async def setOutputDataRates(byteArray):
    print("First Enable Sensor Value Data Rate")
    default = bytearray(await getAllSTEConfig())
    print(default , " 5. index" , bytearray(default[5]))
    default[5] = byteArray[0]
    await client.write_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"],default) 
    print("setOutputDataRates Function set Value Data Rate")
    print(await getOutputDataRates())  


# Dataların flash memorye yazılması ile ilgili kısımdır aktifleştirme ve hangi sensörlerin seçileceği ile ilgili
# 0xF1 accelerRaw enable 
# 0xF5 acceler and light enable
# 0xF0 all disabled
# 0xFF enable all 
async def setSensorRawValueToFlash(byteArray):
    print("First Enable Sensor Value for Flash Raw")
    default =  bytearray(await getAllSTEConfig())
    print(default[30])
    default[30] = byteArray[0]
    #default[30] = bytearray((241).to_bytes(1, byteorder='big'))[0]
    await client.write_gatt_char(ServiceShortTermExperiment["STEConfigurationParameters"],default) 
    print("Sensor Speed setSensorRawValueToFlash Function")
    print(await getOutputDataRates())  


###########################################################################################################################


###################################     BULK  DATA TRANSFER (BDT)     ######################################################

# BDT DATA Transfer Control 1 byte 
# 0 olursa değeri go to idle  0x00
# 1 olursa start transfer of sensor data 0xFF 
# buradaki 1 ve 0 değerleri hex olarak verilmemiştir sadece tahmindir !!!


async def setBDTControl(oneByte): # Burası SADECE YAZILABİLİRDİR
    return await client.write_gatt_char(ServiceBulkDataTransfer["BulkDataTransferControl"],oneByte)


# BDT veri akışını okuma için hem üye olma hem de read 
async def getDataFlowRead(): # Burası SADECE YAZILABİLİRDİR
    return await client.read_gatt_char(ServiceBulkDataTransfer["BulkDataTransferDataFlow"])
    

async def getDataFlowNotify(): # Burası SADECE YAZILABİLİRDİR
 
    await client.start_notify(ServiceBulkDataTransfer["BulkDataTransferDataFlow"] , notification_handler)
    await setBDTControl(b'\x01')
    firsLenght = len(allNotifiy)
    counterL = 0
    second = 0
    while(1 ):
        try:    
          
            if counterL %10 == 0 :    
                firsLenght = len(allNotifiy)
                counterL = 0
            if second == firsLenght and firsLenght != 0:
                break
            if len(allNotifiy)!=0 and len(allNotifiy) ==  int.from_bytes(bytearray(allNotifiy[0])[4:8] , "little"):
                break
            await asyncio.sleep(1.0)
            counterL +=1
            second = len(allNotifiy)
        except:
            print("Download Error , some problem occure ")
    loop.run_until_complete(client.stop_notify(ServiceBulkDataTransfer["BulkDataTransferDataFlow"]))
    print("Notify lenght : " , len(allNotifiy))
  
# Statüsünü okuma bu SADECE OKUNABİLİRDİR !!!
# 0 : Idle
# 1 : Transfer ongoing Datanın SCD üzerinden bağlanılan cihaza gittiğini gösterir
# 2 : Transfer bitti anlamı taşır
# 3 : BDT Error data yollanamamıştır. SCD de bir hata oluşmuştur.
async def getDataFlowStatus(): # Burası SADECE YAZILABİLİRDİR
    return await client.read_gatt_char(ServiceBulkDataTransfer["BulkDataTransferStatus"])

async def startDownload():
    await connectWithCheck()
    print("Downloand started")
    await getDataFlowNotify()
    await disconnect()


########################################################################################################################

################################################## LOGGING BAŞLAMA VE BİTİRME FONKSİYONLARI ############################
    

async def saveDataInFlash(speed,  recordTime): # kayıt için gerekli olan tek şey , dahili hafıza silme hangi sensörlerin kayıt alıcağı ve ne kadar zaman alacağı yollanır
    # x01 Acceler
    # x02 Magnemeter
    # x04 Light
    # x08 Temperature
    print("Erase started")
    await deleteFlashMemory()
    await connectWithCheck()
    await stopToggle()
    await setSensorsEnables(b'\xf0')
    await setSensorsEnables(b'\x01')
    await setOutputDataRates(speed[0])
    await setSensorRawValueToFlash(b'\xf1')
    print("Record started")
    await startToggle()
    time.sleep(recordTime)
    await stopToggle()
    print("Record finished")
    await disconnect()
    await startDownload()

################################################### GENERAL FUNCTIONS NOT SPECIAL ###########################################
NameMap = {}
async def scanDevice():
    devices = await BleakScanner.discover()
    for d in devices:
        NameMap[d.name] = d.address

async def getDevice(ble_address):
    device = await BleakScanner.find_device_by_address(ble_address, timeout=5.0)
    return device

async def connect():
    await client.connect()
    print("Connected")

async def disconnect():
    await client.disconnect()
    print("Disconnected")

async def checkDevice():
    NameMap.clear()
    await scanDevice()
    for i in NameMap.values():
        if i == "18:04:ED:62:5B:B6":
            return True
    return False

async def connectWithCheck():
    while(True ):
        if await checkDevice():
           break
    await connect()




async def periodicTime(recordTime , waitTime , speed):
    mainControlArr = secondSettingBlock()
    while(mainControlArr[15]):
        try:
            mainControlArr = secondSettingBlock()
            print("-----star---- Periodt")
            await connect()
            #await setModeSelection(True)
            global allNotifiy
            allNotifiy= []
            print("Erase memory")
            await deleteFlashMemory()
            await disconnect()
            await connectWithCheck()
            await stopToggle()
            await setSensorsEnables(b'\xf0')
            await setSensorsEnables(b'\x01')
            await setOutputDataRates(speed)
            await setSensorRawValueToFlash(b'\xf1')
            print("Sensör start recording")
            await startToggle()
            time.sleep(recordTime)
            print("Sensör stop recording")
            await stopToggle()
            await disconnect()
            await connectWithCheck()
            await startToggle()
            print("Download is starting")
            await getDataFlowNotify()
            await disconnect()
            await disconnect()
            print("All task is successfully")
            time.sleep(waitTime)
        except Exception as e:
            #print(e)
            controlF = await checkDevice()
            if controlF:
                if await client.is_connected():
                    await disconnect()
                    await testPeriodic()
                else:
                    await disconnect()
                    print("Somethings went wrong ! ")
                    await testPeriodic()
            else:
                print("Device Closed")


async def testPeriodic():
    mainControlArr = secondSettingBlock()
    while(mainControlArr[15]):
        try:
            mainControlArr = secondSettingBlock()
            print("-----star---- Periodt")
            await connect()
            #await setModeSelection(True)
            global allNotifiy
            allNotifiy= []
            print("Erase memory")
            await deleteFlashMemory()
            await disconnect()
            await connectWithCheck()
            await stopToggle()
            await setSensorsEnables(b'\xf0')
            await setSensorsEnables(b'\x01')
            await setOutputDataRates(b'\x00')
            await setSensorRawValueToFlash(b'\xf1')
            print("Sensör start recording")
            await startToggle()
            time.sleep(5)
            print("Sensör stop recording")
            await stopToggle()
            await disconnect()
            await connectWithCheck()
            await startToggle()
            print("Download is starting")
            await getDataFlowNotify()
            await getSTEResultNotify()
            await disconnect()
            print("All task is successfully")
        except Exception as e:
            #print(e)
            controlF = await checkDevice()
            if controlF:
                if await client.is_connected():
                    await disconnect()
                    await testPeriodic()
                else:
                    await disconnect()
                    print("Somethings went wrong ! ")
                    await testPeriodic()
            else:
                print("Device Closed")
  
loop = asyncio.get_event_loop()
loop.run_until_complete(scanDevice())
client = BleakClient("18:04:ED:62:5B:B6") # Adres girilmesi lazım
#client = BleakClient("18:04:ED:62:5B:AC") # Adres girilmesi lazım






