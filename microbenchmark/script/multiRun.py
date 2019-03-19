#!/usr/bin/env python

from pythonLib.readConfig import readConfig
from pythonLib.swapDevMount import swapDevMount
import subprocess 
import datetime
import time
import os
import xlwt

DEBUG=True
ConfigFileName='z_config'
TempStatFile = 'z_autoTest.stat'

def doDisableTest(timeStamp,config):
    subprocess.Popen(['systemctl','disable',config['OSSystemdPath']]).wait()
    subprocess.Popen(['rm',config['RootPath']+TempStatFile]).wait()
    subprocess.Popen(['cp',config['RootPath']+ConfigFileName,
                      config['LogFolderPath']+timeStamp+'/'+ConfigFileName]).wait()
    subprocess.Popen(['cp',config['RootPath']+config['FilterFuncfile'],
                      config['LogFolderPath']+timeStamp+'/'+config['FilterFuncfile']]).wait()

    if config['FtraceOn'] == 'True':
        # Tar ftrace log
        os.system('tar -zcvf '+ config['LogFolderPath'] + timeStamp + '/' + \
                  'ftrace.tar.gz ' + config['LogFolderPath'] + timeStamp + '/' + 'ftrace/*')
        os.system('rm -rf '+ config['LogFolderPath'] + timeStamp + '/' + 'ftrace/')

    os.system('mail -s "' + timeStamp + ' Test Complete" ' + config['MailList'] +  ' < /dev/null')

def writeStat(doneConfig,config):
    flag=True
    # doneConfig=[Round,Device,Size,LogPath]

    # Check the next test size will over the limit or not.
    # Check this is the last round or not.

    if config['TestMethod'] == 'list':
        doNextConfig = doneConfig
        testList = config['TestList'].split(',')
        curIndex = testList.index(str(doneConfig[2]))
        if curIndex == len(testList) - 1:
            if doneConfig[0] ==  int(config['Round']):
                doDisableTest(doneConfig[3],config)
                flag=False
            # Next Round
            else:
                doNextConfig[0] = doneConfig[0] + 1
                doNextConfig[2] = testList[0]
        else:
            doNextConfig[2] = testList[curIndex+1]
  
    elif config['TestMethod'] == 'diff':
        doNextConfig = doneConfig
        if doneConfig[2] + int(config['DiffSize']) > int(config['EndSize']):
            if doneConfig[0] ==  int(config['Round']):
                doDisableTest(doneConfig[3],config)
                flag=False
            # Next Round
            else:
                doNextConfig[0] = doneConfig[0] + 1
                doNextConfig[2] = int(config['InitSize'])
        else:
            doNextConfig[2] = doneConfig[2] + int(config['DiffSize'])

    if flag:
        file = open(config['RootPath']+TempStatFile, 'w+')
        for item in doNextConfig:
            file.write(str(item)+' ')
        file.close

    return flag

def checkCurStat(config):
    '''
    doConfig=[current round, test device, test size, log folder]
    '''
    if os.path.exists(config['RootPath']+TempStatFile):
        file = open(config['RootPath']+TempStatFile, 'r')
        doConfig = file.readline().split()
        doConfig[0] = int(doConfig[0])
        doConfig[2] = int(doConfig[2])
        file.close()
    else:
        ts = time.time()
        timeStamp=datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
        if config['TestMethod'] == 'list':
            doConfig = [1, config['TestDev'], int(config['TestList'].split(',')[0]),timeStamp]
        elif config['TestMethod'] == 'diff':
            doConfig = [1,config['TestDev'],int(config['InitSize']),timeStamp]
        else:
            return 1
        folderName=config['LogFolders'].split(',')
        for name in folderName:
            os.makedirs(config['LogFolderPath']+ timeStamp + '/' + name+'/')

    return doConfig

if __name__ == '__main__':
    '''
    while True:
        obj = readConfig(os.path.dirname(os.path.realpath(__file__)) +'/' + ConfigFileName)
        config = obj.getConfig()
        config['TestDev'] = swapDevMount(config['TestDev']).getDev()
        doConfig=checkCurStat(config)
        if DEBUG:
            print doConfig
        
        subprocess.Popen(['/bin/bash',config['RootPath']+config['ScriptFile'],
                           str(doConfig[0]),doConfig[1],str(doConfig[2]),doConfig[3]).wait()
        writeStat(doConfig,config)
        if DEBUG:
            print 'TestDev = ' + config['TestDev']
            os.system('swapoff /dev/' + config['TestDev'])
            os.system('iscsiadm -m node --logout')
        if writeStat(doConfig,config) == False:
            break
        #os.system('/sbin/reboot')
    '''
    obj = readConfig(os.path.dirname(os.path.realpath(__file__)) +'/' + ConfigFileName)
    config = obj.getConfig()
    config['TestDev'] = swapDevMount(config['TestDev']).getDev()
    doConfig=checkCurStat(config)
    subprocess.Popen(['/bin/bash',config['RootPath']+config['ScriptFile'],
                     str(doConfig[0]),doConfig[1],str(doConfig[2]),doConfig[3]]).wait()
    if DEBUG:
        print doConfig
        print 'TestDev = ' + config['TestDev']
        os.system('swapoff /dev/' + config['TestDev'])
        os.system('iscsiadm -m node --logout')
    writeStat(doConfig,config)
    os.system('/sbin/reboot')
