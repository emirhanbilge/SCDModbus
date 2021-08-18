import sys , time 
sys.path.append('../')
from manageSCD import testPeriodic , loop
import automatePairing as a
import threading
from modbusServer import run_async_server 

""" Automate Pairing Thread - Start"""
def automate_pairing():
    agent = a.Agent(a.bus, a.AGENT_PATH)
    agnt_mngr = a.dbus.Interface(a.bus.get_object(a.BUS_NAME, a.AGNT_MNGR_PATH),
                               a.AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(a.AGENT_PATH, a.CAPABILITY)
    agnt_mngr.RequestDefaultAgent(a.AGENT_PATH)

    adapter = a.Adapter()
    global mainloop  
    mainloop = a.GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(a.AGENT_PATH)
        mainloop.quit()   

t1 = threading.Thread(target= automate_pairing)
t1.start()
""" Automate Pairing Thread - End"""
count = 1

t2 = threading.Thread(target= run_async_server)
t2.start()
while(1):
    print("Loop sayısı " , count)
    loop.run_until_complete(testPeriodic())
    count +=1
#testPeriodic
mainloop.quit()  


















"""
startDTime = time.localtime(time.time())

loop.run_until_complete(connect())

loop.run_until_complete(saveDataInFlash(b'\xf1', 8 ))

loop.run_until_complete(startDownload())
finishDTime = time.localtime(time.time())
"""















#print("İndirme zamanı" , finishDTime.tm_min-startDTime.tm_min," dakika saniye : " ,finishDTime.tm_sec-startDTime.tm_sec )
#startDTime = time.localtime(time.time())
"""
while(1):
    startDTime = time.localtime(time.time())
    loop.run_until_complete(connect())
    loop.run_until_complete(saveDataInFlash(b'\xf1',20 ))
    loop.run_until_complete(startDownload())
    finishDTime = time.localtime(time.time())
    print("İndirme zamanı" , finishDTime.tm_min-startDTime.tm_min," dakika saniye : " ,finishDTime.tm_sec-startDTime.tm_sec )
    startDTime = time.localtime(time.time())
    loop.run_until_complete(connect())
    loop.run_until_complete(getSTEResultNotify())
    finishDTime = time.localtime(time.time())
    print("Canlı Yayın zamanı" , finishDTime.tm_min-startDTime.tm_min," dakika saniye : " ,finishDTime.tm_sec-startDTime.tm_sec)
    loop.run_until_complete(disconnect())
"""


"""
convertByteArr("output.txt")
getX_Y_Z()
print("8888888888888888")
"""

"""
loop.run_until_complete(setSensorsEnables(b'\xff'))
loop.run_until_complete(disconnect())
loop.run_until_complete(connect())
"""


"""
loop.run_until_complete(setSensorsEnables(b'\xff'))
loop.run_until_complete(stopToggle())
loop.run_until_complete(setOutputDataRates(b'\x02'))
loop.run_until_complete(startToggle())
print(loop.run_until_complete(getAllSTEConfig()))
loop.run_until_complete(getSTEResultNotify())
print(loop.run_until_complete(getAllSTEConfig()))
loop.run_until_complete(disconnect())
"""
""" +-+++++++++++++++++++++++++++
loop.run_until_complete(connect())

loop.run_until_complete(testPeriodic())
"""
#loop.run_until_complete(startDownload())


"""
counter = 0
while(1):
    timeS = time.time()
    
    print( time.time()-timeS)
"""
"""
print("Erase started")
await deleteFlashMemory()
await disconnect()
time.sleep(9)
await connect()
print("Record started")
await (setSensorRawValueToFlash(b'\xf1'))
    #time.sleep(10)
await startToggle()
time.sleep(recordTime)
await stopToggle()
await disconnect()
"""