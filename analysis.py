#!/usr/bin/python3
import os
import time
import subprocess
import serial

# configuration

## paths
PICO_MOUNT_POINT = '/media/mahdif/RPI-RP2/' # TODO: hardcoded
BUILD_DIR = './build' # TODO: hardcoded

## serial port
SERIAL_PORT_NAME = '/dev/ttyACM0'
SERIAL_PORT_BAUDRATE = 115200

## commmunication
INTERVAL_COUNT = 1
INTERVAL_SEC = 12
TIMEOUT_SEC = 0.5
STAT_SIZE = 4000

# constants

CONNECTION_DELAY = 2
BUILD_UF2 = BUILD_DIR + '/demo.uf2' # TODO: UNIX-specific
JOB_COUNT = os.cpu_count()
BUILD_COMMAND = 'cmake --build {} --parallel {}'.format(BUILD_DIR,JOB_COUNT)
LOAD_COMMAND = 'cp {} {}'.format(BUILD_UF2,PICO_MOUNT_POINT) # TODO: UNIX-specific



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
print(input)