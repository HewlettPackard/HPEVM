#!/usr/bin/env python

import subprocess 
import datetime
import time
import os
import xlwt

ConfigFilePath='/home/tdc/Documents/ftrace/5_autotest/script/z_config'
FuncTraceListPath='/home/tdc/Documents/ftrace/5_autotest/script/z_filter_function'
StatusFilePath='/home/tdc/Documents/ftrace/5_autotest/z_autoTest.stat'
TestFolderPath='/home/tdc/Documents/ftrace/5_autotest/'
MailingListFile='/home/tdc/Documents/ftrace/5_autotest/script/z_mailList'
OSSystemdPath='/lib/systemd/system/autoGenPagingLog.service'
ScriptPath='/home/tdc/Documents/ftrace/5_autotest/script/pid_trace.sh'
TestDev={'sdc':1,'sdb':2}
FolderName=['meminfo']
NumberDev=2
DEBUG=True

class dataParser:
    def __init__(self,ConfigFilePath,devList):
        configfile = open(ConfigFilePath, 'r')
        config = configfile.read().splitlines()
        self.config = filter(None, config)
        self.meminfo = ['User time (seconds):',
                        'System time (seconds):',
                        'Percent of CPU this job got:',
                        'Elapsed (wall clock) time (h:mm:ss or m:ss):',
                        'IOWait:']
        self.fileType=['ftd','meminfo']
        self.devList=devList

    def getDataFormFile(self, filePath, fileType):
        if fileType == self.fileType[0]:
            ftdList = []
            rFile = open(filePath, 'r')
            for line in rFile:
                for item in self.config:
                    if item in line:
                        ftdList.append(line.split())
            #if DEBUG:
            #    print 'ftdList:',ftdList
            rFile.close()
            return {fileType:ftdList}

        elif fileType == self.fileType[1]:
            meminfoList = []
            rFile = open(filePath, 'r')
            for line in rFile:
                for item in self.meminfo:
                    if item in line:
                        meminfoList.append([item,line[len(item)+2:len(line)-2]])
            #if DEBUG:
            #    print 'meminfoList:',meminfoList
            rFile.close()
            return {fileType:meminfoList}
        else:
            pass

    def getConfigInfo(self):
        return self.config

    def doDataTable(self,data,table):
        '''
        # Do ftd part
        print data[self.devList[0]][self.fileType[0]].sort()
        print data[self.devList[1]][self.fileType[0]].sort()

        # Do write some information
        ftdEntryLen = 6
        ftdEntryName=['Count','Time','Average','Local','Std_dev']
        table.write(0,0,'hdd_'+self.devList[0])
        table.write(0,6,'rdma_'+self.devList[1])
        table.write(0,12,'hdd/rdma')

        for i in range(len(ftdEntryName)):
            table.write(0,i+1,ftdEntryName[i])
            table.write(0,i+1+ftdEntryLen,ftdEntryName[i])
            table.write(0,i+1+ftdEntryLen*2,ftdEntryName[i])

        if len(data[self.devList[0]][self.fileType[0]]) == len(data[self.devList[1]][self.fileType[0]]):
            length= len(data[self.devList[0]][self.fileType[0]])
            for i in range(length):
                for j in range(ftdEntryLen):
                    dataDev = 0
                    if j != 0:
                        dataDev0 = float(data[self.devList[0]][self.fileType[0]][i][j])
                        dataDev1 = float(data[self.devList[1]][self.fileType[0]][i][j])
                        if dataDev1 != 0:
                            dataDev = float(dataDev0/dataDev1)

                    table.write(i+1,j,data[self.devList[0]][self.fileType[0]][i][j])
                    table.write(i+1,j+ftdEntryLen,data[self.devList[1]][self.fileType[0]][i][j])
                    table.write(i+1,j+ftdEntryLen*2,dataDev)

        else:
            length= len(data[self.devList[0]][self.fileType[0]])
            for i in range(length):
                for j in range(ftdEntryLen):
                    table.write(i+1,j,data[self.devList[0]][self.fileType[0]][i][j])

            length= len(data[self.devList[1]][self.fileType[0]])
            for i in range(length):
                for j in range(ftdEntryLen):
                    table.write(i+1,j+ftdEntryLen,data[self.devList[1]][self.fileType[0]][i][j])
        '''
        # Do meminfo data write
        meminfoInitRaw = len(self.config) + 5
        meminfoEntryLen = 2
        table.write(meminfoInitRaw,0,'hdd_'+self.devList[0])
        table.write(meminfoInitRaw,2,'rdma_'+self.devList[1])
        table.write(meminfoInitRaw,4,'hdd/rdma')

        ioWaitTime0 = 0.0
        ioWaitTime1 = 0.0
        for i in range(len(self.meminfo)):
            # For IOWait. Doing it in here to avoid index overflow
            if i == len(self.meminfo) - 1 :
                table.write(meminfoInitRaw+i+1,0,self.meminfo[i])
                table.write(meminfoInitRaw+i+1,meminfoEntryLen,self.meminfo[i])

                table.write(meminfoInitRaw+i+1,1,ioWaitTime0)
                table.write(meminfoInitRaw+i+1,1+meminfoEntryLen,ioWaitTime1)
                if ioWaitTime1 != 0:
                    table.write(meminfoInitRaw+i+1,1+meminfoEntryLen*2,ioWaitTime0/ioWaitTime1)
                else:
                    table.write(meminfoInitRaw+i+1,1+meminfoEntryLen*2,'N/A')
                break
            for j in range(meminfoEntryLen):
                dataDev = 0
                if j != 0:
                    if i == len(self.meminfo) - 2 : # For Elapsed time:
                        dataDev0 = data[self.devList[0]][self.fileType[1]][i][j].split(':')
                        dataDev0 = 60*float(dataDev0[0])+float(dataDev0[1])
                        dataDev1 = data[self.devList[1]][self.fileType[1]][i][j].split(':')
                        dataDev1 = 60*float(dataDev1[0])+float(dataDev1[1])
                        dataDev = float(dataDev0/dataDev1)
                        # Get IOWait time by total time minus system time
                        ioWaitTime0 = dataDev0 - ioWaitTime0
                        ioWaitTime1 = dataDev1 - ioWaitTime1    
                    else:
                        dataDev0 = float(data[self.devList[0]][self.fileType[1]][i][j])
                        dataDev1 = float(data[self.devList[1]][self.fileType[1]][i][j])
                        if dataDev1 != 0:
                            dataDev = float(dataDev0/dataDev1)
                        if i != 2: # Get rid of Percent of CPU
                            ioWaitTime0 += dataDev0
                            ioWaitTime1 += dataDev1
                table.write(meminfoInitRaw+i+1,j,data[self.devList[0]][self.fileType[1]][i][j])
                table.write(meminfoInitRaw+i+1,j+meminfoEntryLen,data[self.devList[1]][self.fileType[1]][i][j])
                table.write(meminfoInitRaw+i+1,j+meminfoEntryLen*2,dataDev)

def doAnalysis(roundTime,timeStamp,config):
    size = config[0]
    doWork = dataParser(FuncTraceListPath,TestDev.keys())
    excel = xlwt.Workbook()

    sumTable = excel.add_sheet('SUM',cell_overwrite_ok=True)
    totalTablesNum = []
    tableNum = 1

    testList = [262144, 314573, 367002, 524288, 786432, 1048576]
    # Create data table for each size
    #while size <= config[2]:
    for size in testList:
        # Write size to sum table on raw 0
        sumTable.write(0,tableNum,str(size))
        tableNum += 1
        totalTablesNum.append(str(size))
        
        table = excel.add_sheet(str(size),cell_overwrite_ok=True)
        data = {}
        for dev in TestDev.keys():
            data[dev] = {}
            for name in FolderName:
                path = TestFolderPath + 'log/'+ timeStamp + '/' + name + '/pid_trace_' + name + '_' + \
                       dev + '_' + str(roundTime) + '_' + str(size)+'.log'
                if DEBUG:
                    print path
                data[dev].update(doWork.getDataFormFile(path,name))
        doWork.doDataTable(data,table) 
        #print data
        #size += config[1]


    FirstColumnItems = ['Workload Size:','Elapsed Time(RDMA/RAM):','IO Wait Time(RDMA/RAM):']
    # For meminfo location, it is the sum of length of trace funtions, the interval 5 + 1(index from 1 not 0),   
    # and the length of meminfo items.
    DataColumnLocation = ['F'+ str(len(doWork.getConfigInfo())+5+5),
                          'F'+ str(len(doWork.getConfigInfo())+6+5)]

    # Create the first column items
    RequiredEntries = ['Time(HDD/RDMA):','AVE(HDD/RDMA):','Local(HDD/RDMA):','HDD_STD','RDMA_STD']
    # Function data location starts from raw 2
    dataTableLocationCol = ['O','P','Q','F','L']
    dataTableLocationRaw = 2
    
    functionList = doWork.getConfigInfo()
    functionList.sort()
    print functionList
    for i in functionList:
        z = 0
        for j in RequiredEntries:
            FirstColumnItems.append(i + '::' + j)
            DataColumnLocation.append(dataTableLocationCol[z] + str(dataTableLocationRaw))
            z += 1
        dataTableLocationRaw += 1

    for i in range(len(FirstColumnItems)):
         sumTable.write(i,0,FirstColumnItems[i])

    # Fill up the summary table
    letterOrder = 'BCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(len(totalTablesNum)):
        for j in range(len(DataColumnLocation)):
             sumTable.write(j+1,i+1, xlwt.Formula("SUM('"+ str(i+1) +"'!$"+DataColumnLocation[j]+")"))
    excel.save(TestFolderPath + 'log/' + timeStamp + '/Round' + str(roundTime) +'.xls')


if __name__ == '__main__':
    
    # For creating the excel file only can use the following command
    doAnalysis(1,'20180202_O1RAMRDMA',[8,2,40,1])
    
