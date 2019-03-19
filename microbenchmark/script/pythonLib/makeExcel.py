#! /usr/bin/env python

import readConfig
import subprocess 
import datetime
import time
import os
import xlwt

ConfigFileName = 'z_config'
SupportDataType = ['ftd','meminfo']
RoundNumber = 5
DEBUG = 1

class makeExcel:
    def __init__(self,folderPath1,folderPath2,dataType,method='1on1'):
        self.meminfoSample = ['User time (seconds):',
                              'System time (seconds):',
                              'Percent of CPU this job got:',
                              'Elapsed (wall clock) time (h:mm:ss or m:ss):',
                              'IOWait:']
        # Could be modify at createPathMapping method.
        self.ftdFilterPath = folderPath1 + '/z_filter_function'
        self.ftdSample = None
        self.ftdFuncHeader = None # This will be filled at getftdData

        # Data configuration infomation
        self.dataObj1 = None       
        self.dataObj2 = None

        self.folderPath1 = folderPath1
        self.folderPath2 = folderPath2
        self.dataType = dataType.split(',')
        self.method = method
        self.sizeList = None
        self.status = True        

        if os.path.exists(folderPath1+'/'+ConfigFileName) and \
           os.path.exists(folderPath2+'/'+ConfigFileName):
            for item in dataType.split(','):
                if item not in SupportDataType:
                    print 'Unsupported datatpye'
                    self.status = False
            
        else:
            print 'The config file,'+ConfigFileName+' is not locate at the either pathes'
            self.status = False

        self.getRequiredInfo()
        
    def getRequiredInfo(self):
        self.dataObj1 = dataObj1 = readConfig.readConfig(self.folderPath1 + '/' + ConfigFileName).getConfig()
        self.dataObj2 = dataObj2 = readConfig.readConfig(self.folderPath2 + '/' + ConfigFileName).getConfig()

        for dataType in self.dataType:
            if self.sizeList == None:
                data = sorted([f for f in os.listdir(self.folderPath1+'/'+dataType) if '_1_' in f],
                              key = lambda x:int(x.split('_')[5].split('.')[0]))
                self.sizeList = map(lambda x:x.split('_')[5].split('.')[0], data)
            if dataType == 'ftd':
                rfile = open(self.ftdFilterPath, 'r')
                self.ftdSample = filter(None, rfile.read().splitlines())
                rfile.close()


    def createPathMapping(self):
        dataObj1 = self.dataObj1
        dataObj2 = self.dataObj2

        self.ftdFilterPath = self.folderPath1 + '/' + dataObj1['FilterFuncfile']

        typeMatch = False
        if dataObj1['TestMethod'] == dataObj2['TestMethod']: 
            if (dataObj1['TestMethod'] == 'list' and dataObj1['TestList'] == dataObj2['TestList']) or \
               (dataObj1['TestMethod'] == 'diff' and \
                dataObj1['InitSize'] == dataObj2['InitSize'] and \
                dataObj1['DiffSize'] == dataObj2['DiffSize'] and \
                dataObj1['EndSize'] == dataObj2['EndSize'] ):
                typeMatch = True
            else:
                print 'The two test methods(list,diff) configurations are not matched'        
        else:
            print 'Those two test methods(list,diff) are not matched'
        
        pathList1 = {}
        pathList2 = {}
        if typeMatch and self.method == '1on1':
            if dataObj1['Round'] == dataObj2['Round']:
                for i in self.dataType:          
                    pathList1[i] = self.getFileList(self.folderPath1, i, int(dataObj1['Round']), 1)
                    pathList2[i] = self.getFileList(self.folderPath2, i, int(dataObj2['Round']), 1)
        elif typeMatch and self.method == '1toN':
            for i in self.dataType:
                pathList1[i] = self.getFileList(self.folderPath1, i, 1, int(dataObj2['Round']))
                pathList2[i] = self.getFileList(self.folderPath2, i, int(dataObj2['Round']), 1)
        elif typeMatch and self.method == 'Nto1':
            for i in self.dataType:
                pathList1[i] = self.getFileList(self.folderPath1, i, int(dataObj1['Round']), 1)
                pathList2[i] = self.getFileList(self.folderPath2, i, 1 , int(dataObj1['Round']))
        else:
            print 'Unsupport mapping method. EX: 1on1,1toN,Nto1'
            return []
        
        # pathList = {'dataType':[pathListSorted=[round1],[round2],...]}
        return [pathList1,pathList2]

    def getFileList(self, path, dataType, times, redundant):
        data = []
        for i in range(times):
            data.append(sorted([f for f in os.listdir(path+'/'+dataType) if '_'+ str(i+1) +'_' in f],
                        key=lambda x:int(x.split('_')[5].split('.')[0])))
        
        if redundant > 1 :
            for i in range(redundant - 1):
                data.append(data[0])

        return data

    def getData(self,path,dataType):
        if dataType == 'ftd':    
            return self.getftdData(path)
        elif dataType == 'meminfo':
            return self.getmeminfoData(path)
        else:
            pass

    def getftdData(self,path):
        rfile = open(path, 'r')
        reData = {}
        for line in rfile:
            for item in self.ftdSample:
                if item in line:
                    reData[item] = map(int,line.split()[1:])
                elif self.ftdFuncHeader == None and 'Function' in line:
                    self.ftdFuncHeader = line.split()[1:]
        return reData

    def getmeminfoData(self,path):
        rfile = open(path, 'r')
        reData = {}
	if DEBUG == 1:
		print path
        for line in rfile:
            for item in self.meminfoSample:
                if item in line:
                    if item == 'Elapsed (wall clock) time (h:mm:ss or m:ss):':
                        tmp = line[len(item)+2:len(line)-2].split(':')
                        if len(tmp) == 2 :
                            reData[item] = 60*float(tmp[0])+float(tmp[1])
                        else:
                            reData[item] = 3600*float(tmp[0])+60*float(tmp[1])+float(tmp[2])
                    else:
                        reData[item] = float(line[len(item)+2:len(line)-2])
        reData['IOWait:'] = reData['Elapsed (wall clock) time (h:mm:ss or m:ss):'] - \
                            reData['User time (seconds):'] - \
                            reData['System time (seconds):']
        return reData

    def compareData(self,data1,data2,dataType):
        if dataType == 'ftd':
            return self.compareftdData(data1,data2)
        elif dataType == 'meminfo':
            return self.comparememinfoData(data1,data2)
        else:
            pass

    def compareftdData(self,data1,data2):
        reData = {}
        div = lambda x,y: round(float(x)/float(y),RoundNumber) if y!=0 else 'N/A'
        for item in self.ftdSample:
            if item in data1 and item in data2:
                reData[item] = [ div(x,y) for x, y in zip(data1[item],data2[item])]
        return reData
    
    def comparememinfoData(self,data1,data2):
        reData = {}
        div = lambda x,y: round(float(x)/float(y),RoundNumber) if y!=0 else 'N/A'
        for item in self.meminfoSample:
            if item in data1 and item in data2:
                reData[item] = round(div(data1[item],data2[item]),RoundNumber)
        return reData

    def writeTable(self):
        [pathList1,pathList2] = self.createPathMapping()
        for time in range(max(int(self.dataObj1['Round']),int(self.dataObj2['Round']))):
            excel = xlwt.Workbook()
            sumTable = excel.add_sheet('SUM',cell_overwrite_ok=True)
            [rawSumPage,colSumPage] = [0,1]
            for sizeIndex in range(len(self.sizeList)):
                table = excel.add_sheet(self.sizeList[sizeIndex],cell_overwrite_ok=True)
                rawSizePage = 0
                for dataType in self.dataType:
                    data1 = self.getData(self.folderPath1+dataType+'/'+pathList1[dataType][time][sizeIndex],dataType)
                    data2 = self.getData(self.folderPath2+dataType+'/'+pathList2[dataType][time][sizeIndex],dataType)
                    dataCom = self.compareData(data1,data2,dataType)
                    rawSizePage = self.writeSizePage(table,data1,data2,dataCom,dataType,rawSizePage)
                    rawSumPage = self.writeSumPage(sumTable,dataCom,self.sizeList[sizeIndex], \
                                                              dataType,rawSumPage,colSumPage)
                [rawSumPage,colSumPage] = [0,colSumPage+1] 
                
            excel.save( 'Round_'+str(time+1) +'.xls')

    def writeSizePage(self,table,data1,data2,dataCom,dataType,rawSizePage):
        if dataType == 'ftd':
            # ftd first line
            table.write(rawSizePage,0,self.dataObj1['TestDev'])
            table.write(rawSizePage,len(self.ftdFuncHeader)+1,self.dataObj2['TestDev'])
            table.write(rawSizePage,len(self.ftdFuncHeader)*2+2,self.dataObj1['TestDev'] + \
                                                               '/' + self.dataObj2['TestDev'])
            for i in range(len(self.ftdFuncHeader)):
                table.write(rawSizePage, i + 1, self.ftdFuncHeader[i])
                table.write(rawSizePage, i + 2 + len(self.ftdFuncHeader), self.ftdFuncHeader[i])
                table.write(rawSizePage, i + 3 + len(self.ftdFuncHeader)*2, self.ftdFuncHeader[i])
            
            rawSizePage += 1
            # ftd rest lines      
            for item in self.ftdSample:
                if item in data1:
                    table.write(rawSizePage, 0 , item )
                    for i in range(len(self.ftdFuncHeader)):
                        table.write(rawSizePage, i + 1, str(data1[item][i]))
                if item in data2:
                    table.write(rawSizePage, 0 , item )
                    for i in range(len(self.ftdFuncHeader)):
                        table.write(rawSizePage, i + 2 + len(self.ftdFuncHeader), str(data2[item][i]))
                if item in dataCom:
                    table.write(rawSizePage, 0 , item )
                    for i in range(len(self.ftdFuncHeader)):
                        table.write(rawSizePage, i + 3 + len(self.ftdFuncHeader)*2, str(dataCom[item][i]))
                rawSizePage += 1

        elif dataType == 'meminfo':
            # meminfo first line
            table.write(rawSizePage,0,self.dataObj1['TestDev'])
            table.write(rawSizePage,2,self.dataObj2['TestDev'])
            table.write(rawSizePage,4,self.dataObj1['TestDev'] + '/' + self.dataObj2['TestDev'])
            rawSizePage += 1
            for item in self.meminfoSample:
                table.write(rawSizePage, 0 , item)
                table.write(rawSizePage, 1 , str(data1[item]))
                table.write(rawSizePage, 2 , item)
                table.write(rawSizePage, 3 , str(data2[item]))
                table.write(rawSizePage, 4 , str(dataCom[item]))
                rawSizePage += 1

        return rawSizePage+2

    def writeSumPage(self,sumTable,dataCom,size,dataType,rawSumPage,colSumPage):
        if rawSumPage == 0:
            sumTable.write(0,0,'Workload')
            sumTable.write(0,colSumPage,size)
            rawSumPage += 1

        compStr = '(' + self.dataObj1['TestDev'] + '/' + self.dataObj2['TestDev'] + ')'

        if dataType == 'ftd':
            for item in self.ftdSample:
                for index in range(len(self.ftdFuncHeader)):
                    if colSumPage == 1:  
                        sumTable.write(rawSumPage,0, item + '::' + self.ftdFuncHeader[index] + compStr)
                    if item in dataCom:    
                        sumTable.write(rawSumPage,colSumPage,str(dataCom[item][index]))
                    rawSumPage += 1

        elif dataType == 'meminfo':
            if colSumPage == 1:
                sumTable.write(rawSumPage, 0, 'Elapsed Time' + compStr)
                sumTable.write(rawSumPage + 1, 0, 'IO Wait Time' + compStr)
            sumTable.write(rawSumPage, colSumPage, str(dataCom['Elapsed (wall clock) time (h:mm:ss or m:ss):']))    
            sumTable.write(rawSumPage+1, colSumPage, str(dataCom['IOWait:']))
            rawSumPage += 2           

        return rawSumPage            

if __name__ == '__main__':
    #mod = makeExcel('/home/tdc/Documents/ftrace/5_autotest/log/20180727_154026_FULLRAM_128G-1T_step128G/',
    #                '/home/tdc/Documents/ftrace/5_autotest/log/20180726_191232_RMDA_128G-1T_step128G/',
    #                'meminfo','1toN')
    mod = makeExcel('/home/tdc/Documents/ftrace/5_autotest/log/20180720_162152_FULLRAM_64G-1T/',
                    '/home/tdc/Documents/ftrace/5_autotest/log/20180723_043601_RDMA_64G-1T_step64G/',
                    'meminfo','1toN')
    test = mod.createPathMapping()
    print mod.sizeList
    print '======================================'
    print test[0]
    print '======================================'
    print test[1]
    print '======================================'
    mod.writeTable()
