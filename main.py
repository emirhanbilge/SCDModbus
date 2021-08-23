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






