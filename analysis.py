#!/usr/bin/python3
import os
import sys
import time
import serial
import shutil
from tabulate import tabulate

# paths
BIN_NAME = 'demo.uf2'
# serial port
SERIAL_PORT_BAUDRATE = 115200
# commmunication
INTERVAL_COUNT = 4
INTERVAL_SEC = 6
TIMEOUT_SEC = 0.5
STAT_SIZE = 4000
# connection
CONNECTION_DELAY = 2
# analysis
SCHD_NONSTOP = -1
SCHD_APERIODIC = -2

def secs(x:int):
    return x * 1000 * 1000
def millis(x:int):
    return x * 1000

TASKS = {
    # Log
    'Log': (secs(12),31),
    # Check
    'Check': (secs(3),31),
    # Death
    'CREATOR': (secs(1),3),
    # Interrupt Queue
    'H1QTx': (SCHD_NONSTOP,30),
    'H2QTx': (SCHD_NONSTOP,30),
    'H1QRx': (SCHD_NONSTOP,30),
    'H2QRx': (SCHD_NONSTOP,30),
    'L1QRx': (SCHD_NONSTOP,0),
    'L2QRx': (SCHD_NONSTOP,0),
    # Blocking Queue
    'QConsB1': (SCHD_NONSTOP,2),
    'QProdB2': (SCHD_NONSTOP,0),
    'QConsB3': (SCHD_NONSTOP,0),
    'QProdB4': (SCHD_NONSTOP,2),
    'QProdB5': (SCHD_NONSTOP,0),
    'QConsB6': (SCHD_NONSTOP,0),
    # Counting Semaphores
    'CNT1': (SCHD_NONSTOP,0),
    'CNT2': (SCHD_NONSTOP,0),
    # Math
    'Math1': (SCHD_NONSTOP,0),
    'Math2': (SCHD_NONSTOP,0),
    'Math3': (SCHD_NONSTOP,0),
    'Math4': (SCHD_NONSTOP,0),
    # Generic Queue
    'MuLow': (SCHD_NONSTOP,0),
    'MuMed': (SCHD_NONSTOP,2),
    'MuHigh': (SCHD_NONSTOP,3),
    'MuHigh2': (SCHD_NONSTOP,2),
    'GenQ': (SCHD_NONSTOP,0),
    # Register Check
    'Reg1': (SCHD_NONSTOP,0),
    'Reg2': (SCHD_NONSTOP,0),
    'PolSEM1': (SCHD_NONSTOP,0),
    'PolSEM2': (SCHD_NONSTOP,0),
    'BlkSEM1': (SCHD_NONSTOP,0),
    'BlkSEM2': (SCHD_NONSTOP,0),
    # Recursive Mutex
    'Rec1': (SCHD_NONSTOP,2),
    'Rec2': (SCHD_NONSTOP,1),
    'Rec3': (SCHD_NONSTOP,0),
    # Interrupt Semaphore
    'IntCnt': (SCHD_NONSTOP,0),
    'IntMuS': (SCHD_NONSTOP,1),
    'IntMuM': (SCHD_NONSTOP,0),
    # Task Notify
    'Notified': (SCHD_NONSTOP,0),
    # Queue Overwrite
    'QOver': (SCHD_NONSTOP,0),
    # Timer
    'TmrTst': (SCHD_NONSTOP,30),
    
    # OS
    'IDLE': (SCHD_NONSTOP,0),
    'TmrSvc': (SCHD_APERIODIC,31),
}


def log(mesg:str):
    print('analysis.py: {}'.format(mesg))

def error(mesg:str):
    print('analysis.py: ERROR: {}'.format(mesg))
    exit(1)

def args() -> tuple:
    argv = sys.argv
    if len(argv) < 4:
        exit(1)
    return(argv[1],argv[2],argv[3])

def checkRoot():    
    if os.geteuid() != 0:
        error('root privilege required')

def projectBuild(buildDir):
    buildCommand = 'cmake --build {} --parallel {}'.format(buildDir,os.cpu_count())
    assert(os.system(buildCommand) == 0)
    log('project built')

def projectLoad(buildDir,mountDir):
    shutil.copyfile(
        os.path.join(buildDir,BIN_NAME),
        os.path.join(mountDir, BIN_NAME)
    )
    log('project loaded')

def connectSerialPort(serialPort) -> serial.Serial:
    log('waiting for connection setup')
    time.sleep(CONNECTION_DELAY)
    try:
        serialConnection = serial.Serial(
            port=serialPort,
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

def formatStat(stat):
    [name,execTime] = stat
    (period,priority) = TASKS[name]
    totalTime = INTERVAL_COUNT * secs(INTERVAL_SEC)
    periodCount = totalTime / period
    execTime /= periodCount
    return [name,int(execTime),period,priority]

def isPeriodic(stat):
    t = TASKS[stat[0]][0]
    return t != SCHD_NONSTOP and t != SCHD_APERIODIC

def showSchdAnalysis(stats:list):
    stats.insert(0,['Name','Exec Time','Period','Priority'])
    print(tabulate(stats,headers='firstrow'))
    stats.pop(0)

def showRuntimeStats(stats:list):
    stats.insert(0,['Name','Exec Time'])
    print(tabulate(stats,headers='firstrow'))
    stats.pop(0)

def analysisParameters(stats:list) -> list:
    stats = list(filter(lambda s : isPeriodic(s),stats))
    stats = list(map(lambda s : formatStat(s),stats))
    return stats

def analysisUtilization(stats:list) -> list:
    sum = 0
    for [_,execTime,period,_] in stats:
        sum += execTime/period
    return sum * 100

def main():
    (buildDir, mountDir, serialPort) = args()
    checkRoot()
    projectBuild(buildDir)
    projectLoad(buildDir,mountDir)
    con = connectSerialPort(serialPort)
    stats = readInput(con)
    stats = parseInput(stats)

    print('\nRuntime Stats:')
    showRuntimeStats(stats)

    stats = analysisParameters(stats)
    print('\nScheduling Result:')
    showSchdAnalysis(stats)

    util = analysisUtilization(stats)
    print('\nCPU Utilization: {}%'.format(util))

main()