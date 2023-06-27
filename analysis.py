#!/usr/bin/python3
import os
import time
import subprocess
import serial

# paths
PICO_MOUNT_POINT = '/media/mahdif/RPI-RP2/' # TODO: hardcoded
BUILD_DIR = './build' # TODO: hardcoded
# serial port
SERIAL_PORT_NAME = '/dev/ttyACM0'
SERIAL_PORT_BAUDRATE = 115200
# commmunication
INTERVAL_COUNT = 1
INTERVAL_SEC = 12
TIMEOUT_SEC = 0.5
STAT_SIZE = 4000
# connection
CONNECTION_DELAY = 2
# pipeline
BUILD_UF2 = BUILD_DIR + '/demo.uf2' # TODO: UNIX-specific
JOB_COUNT = os.cpu_count()
BUILD_COMMAND = 'cmake --build {} --parallel {}'.format(BUILD_DIR,JOB_COUNT)
LOAD_COMMAND = 'cp {} {}'.format(BUILD_UF2,PICO_MOUNT_POINT) # TODO: UNIX-specific
# analysis
X = 0
SCHD_IDLE = -1
SCHD_APERIODIC = -2

def secs(x:int):
    return x * 1000 * 1000
def millis(x:int):
    return x * 1000

PERIODS = {
    'Log': secs(12),
    'Check': secs(3),
    'CREATOR': secs(1),
    'H1QTx': SCHD_IDLE,
    'H2QTx': SCHD_IDLE,
    'H1QRx': SCHD_IDLE,
    'H2QRx': SCHD_IDLE,
    'L1QRx': SCHD_IDLE,
    'L2QRx': SCHD_IDLE,
    'QConsB1': SCHD_IDLE,
    'QProdB2': SCHD_IDLE,
    'QConsB3': SCHD_IDLE,
    'QProdB4': SCHD_IDLE,
    'QProdB5': SCHD_IDLE,
    'QConsB6': SCHD_IDLE,
    'CNT1': SCHD_IDLE,
    'CNT2': SCHD_IDLE,
    'Math1': SCHD_IDLE,
    'Math2': SCHD_IDLE,
    'Math3': SCHD_IDLE,
    'Math4': SCHD_IDLE,
    'MuLow': SCHD_IDLE,
    'MuMed': SCHD_IDLE,
    'MuHigh': SCHD_IDLE,
    'MuHigh2': SCHD_IDLE,
    'Reg1': SCHD_IDLE,
    'Reg2': SCHD_IDLE,
    'PolSEM1': SCHD_IDLE,
    'PolSEM2': SCHD_IDLE,
    'BlkSEM1': SCHD_IDLE,
    'BlkSEM2': SCHD_IDLE,
    'Rec1': SCHD_IDLE,
    'Rec2': SCHD_IDLE,
    'Rec3': SCHD_IDLE,
    'IntCnt': SCHD_IDLE,
    'IntMuS': SCHD_IDLE,
    'IntMuM': SCHD_IDLE,
    'GenQ': SCHD_IDLE,
    'QOver': SCHD_IDLE,
    'Notified': SCHD_IDLE,
    'TmrTst': SCHD_IDLE,
    'IDLE': SCHD_IDLE,
    'TmrSvc': SCHD_APERIODIC,
}


def log(mesg:str):
    print('analysis.py: {}'.format(mesg))

def error(mesg:str):
    print('analysis.py: ERROR: {}'.format(mesg))
    exit(1)

def checkRoot():    
    if os.geteuid() != 0:
        error('root privilege required')

def projectBuild():
    assert(os.system(BUILD_COMMAND) == 0)
    log('project built')

def projectLoad():
    assert(os.system(LOAD_COMMAND) == 0)
    log('project loaded')

def connectSerialPort() -> serial.Serial:
    log('waiting for connection setup')
    time.sleep(CONNECTION_DELAY)
    try:
        serialConnection = serial.Serial(
            port=SERIAL_PORT_NAME,
            baudrate=SERIAL_PORT_BAUDRATE
        )
        serialConnection.timeout = TIMEOUT_SEC
        log('connected to RPI-PICO via serial port')
        return serialConnection
    except:
        error('failed to connect to serial port')

def readInput(serialConnection:serial.Serial) -> str:
    input = None
    for i in range(INTERVAL_COUNT):    
        time.sleep(INTERVAL_SEC)
        if i == INTERVAL_COUNT-1:
            data = serialConnection.read(size=STAT_SIZE)
            input = data.decode(encoding='ASCII')
        else:
            serialConnection.read(size=STAT_SIZE)
        log('record ({}/{}) received'.format(i+1, INTERVAL_COUNT))
    return input

def parseInput(input:str) -> str:
    input = input.replace('Tmr Svc','TmrSvc')
    input = input.replace('Tmr Tst','TmrTst')
    input = input.split('\n')
    input = input[4:len(input)-2]
    input = list(map(lambda s : s.split()[0:2],input))
    input = list(map(lambda s : [s[0],int(s[1])*100],input))
    return input

checkRoot()
projectBuild()
projectLoad()
con = connectSerialPort()
input = readInput(con)
input = parseInput(input)
for name in input:
    print(name)