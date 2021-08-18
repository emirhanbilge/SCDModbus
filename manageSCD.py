import asyncio , datetime
from bleak import BleakScanner , BleakClient
import time , datetime
import sys 
import nest_asyncio
nest_asyncio.apply()
sys.path.append('../')
from scdCharacteristic import ServiceBulkDataTransfer,ServiceShortTermExperiment  ,ServiceSCDSettings
from csvFormatter import getX_Y_Z
import modbusServer as mdbs
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient


def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def s16floatfactor(value,factor):
    temp = s16(value[0] | (value[1]<<8))
    temp = float(temp)*factor
    return round(temp,2)
def generate_mdbs_values(listVal):
         
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Little)
        builder.add_16bit_int(listVal[0])    #accelArithmMean_x
        builder.add_16bit_int(listVal[1])    #accelArithmMean_y
        builder.add_16bit_int(listVal[2])    #accelArithmMean_z
        
        payload = builder.to_registers() 
        mdbs.updating_custom_writer(a=(mdbs.Context,),values =payload)
        


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
 
    print(data)
    liveResult = bytearray(data)
    sendModBus = []
    i1 = (int(s16floatfactor(liveResult[0:2],1000)))
    i2 = (int(s16floatfactor(liveResult[2:4],1000)))
    i3 = (int(s16floatfactor(liveResult[4:6],1000)))
    sendModBus.append(i1)
    sendModBus.append(i2)
    sendModBus.append(i3)
    generate_mdbs_values(sendModBus)
    
##########################################################################    DATA SAVE    ##############################################################


def writeDownload():
    clearBytes = []
    lineCounter = 0
    now = datetime.datetime.now()
    nowFileName = str(now.hour) +"."+str(now.minute)+"."+str(now.second)+"."+str(now.day)+"."+str(now.month)+"."+str(now.year)+".txt"
    
    getX_Y_Z(allNotifiy)
    """
    fileO = open(nowFileName,"a")
    for i in allNotifiy:
        if lineCounter > 1:
            
            fileO.write(str(i))
            fileO.write("\n")
            #print(i)
        lineCounter +=1
    """
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
    await client.start_notify(ServiceShortTermExperiment["STEResults"], notificationHandlerResult)
    await asyncio.sleep(10.0)
    await client.stop_notify(ServiceShortTermExperiment["STEResults"])

async def getSTEResultNotifyWithNoTime():
    await client.start_notify(ServiceShortTermExperiment["STEResults"], notificationHandlerResult)

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
    

async def pairDevice():
    await client.pair()

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
    loop.run_until_complete(connect())
    print("Downloand started")
    await getDataFlowNotify()
    await disconnect()


########################################################################################################################

################################################## LOGGING BAŞLAMA VE BİTİRME FONKSİYONLARI ############################
    

async def saveDataInFlash(sensorSelect , recordTime): # kayıt için gerekli olan tek şey , dahili hafıza silme hangi sensörlerin kayıt alıcağı ve ne kadar zaman alacağı yollanır
    # x01 Acceler
    # x02 Magnemeter
    # x04 Light
    # x08 Temperature
    print("Erase started")
    await deleteFlashMemory()
    await disconnect()
    time.sleep(9)
    await connect()
    await stopToggle()
    print("Record started")
    await (setSensorRawValueToFlash(sensorSelect))
    await startToggle()
    time.sleep(recordTime)
    await stopToggle()
    await disconnect()

################################################### GENERAL FUNCTIONS NOT SPECIAL ###########################################
NameMap = {}
async def scanDevice():
    devices = await BleakScanner.discover()
    for d in devices:
        NameMap[d.name] = d.address
    #for i in NameMap.keys():
        #print("Name : ", i , " Mac : " , NameMap[i])


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
            print("Buldu")
            return True
         
    return False

async def connectWithCheck():
    while(True ):
        if await checkDevice():
           break
 
    await connect()

async def testPeriodic():
    try:
        await connect()
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
        startDTime = time.localtime(time.time())
        time.sleep(5)
        print("Sensör stop recording")
        await stopToggle()
        stopDTime = time.localtime(time.time())
        print("Total geçen zaman : dakika " ,(stopDTime.tm_min- startDTime.tm_min) , (stopDTime.tm_sec- startDTime.tm_sec))
        await disconnect()
        await connectWithCheck()
        print("Download is starting")
        await getDataFlowNotify()
        await disconnect()
        print("Result Notify Başlıyacak")
        await startToggle()
        await getSTEResultNotify()
        await stopToggle()
        await startToggle()
        await disconnect()
        print("All task is successfully")
    except:
        controlF = await checkDevice()
        if controlF:
            await disconnect()
            await testPeriodic()
        else:
            print("Cihaz kapandı")
  




loop = asyncio.get_event_loop()
loop.run_until_complete(scanDevice())
client = BleakClient("18:04:ED:62:5B:B6") # Adres girilmesi lazım
#client = BleakClient("18:04:ED:62:5B:AC") # Adres girilmesi lazım






