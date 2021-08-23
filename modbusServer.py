import sys
sys.path.append('../')

# --------------------------------------------------------------------------- # 
# import the various server implementations
# --------------------------------------------------------------------------- #
from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import (ModbusRtuFramer,
                                  ModbusAsciiFramer,
                                  ModbusBinaryFramer)
from custom_message import CustomModbusRequest
# --------------------------------------------------------------------------- # 
# configure the service logging
# --------------------------------------------------------------------------- # 
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()

log.setLevel(logging.CRITICAL)

def updating_writer(a):
    
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x10 #16. word adresi
    values   = []  
    for i in range(1,100):
        values.append(i)
    
    context[slave_id].setValues(register, address, values)

def updating_custom_writer(a,values):
    global Context
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x10 #0. word adresi  

    context[slave_id].setValues(register, address, values) # server da ki 16. word adresinden itibaren values dizisini yükle.

def updating_settings1_writer(a,values):
    global Context
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x42 #0. word adresi

    context[slave_id].setValues(register, address, values) # server da ki 16. word adresinden itibaren values dizisini yükle.

def updating_settings2_writer(a,values):
    global Context
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x43 #0. word adresi

    context[slave_id].setValues(register, address, values) # server da ki 16. word adresinden itibaren values dizisini yükle.
    
def readSettings1(a):
    global Context
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x00 #0. word adresi
    return context[slave_id].getValues(register, 66, 1) # server da ki 16. word adresinden itibaren values dizisini yükle.

def readSettings2(a):
    global Context
    context  = a[0]
    register = 3 # mode 3
    slave_id = 0x00
    address  = 0x00 #0. word adresi
    return context[slave_id].getValues(register, 67, 1) # server da ki 16. word adresinden itibaren values dizisini yükle.


def run_async_server():
    # Modbus kullanılabilir adress dizisini maple
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100))
    store.register(CustomModbusRequest.function_code, 'cm',
                   ModbusSequentialDataBlock(0, [0] * 100))
    global Context
    Context = ModbusServerContext(slaves=store, single=True)
    
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = version.short()

    StartTcpServer(Context, identity=identity, address=("192.168.2.23", 5020),
                   custom_functions=[CustomModbusRequest])
 
if __name__ == "__main__":
    run_async_server()


