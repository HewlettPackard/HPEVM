#!/usr/bin/env python
import os

class readConfig:
    def __init__(self,path):
        self.dataConfig = {}
        if os.path.exists(path):
            rfile = open(path, 'r')
            for line in rfile:
                if '#' not in line and bool(line.rstrip()) == True:
                    self.dataConfig[line.split()[0]] = line.split()[1]
            self.dataConfig['status'] = True
        else:
            self.dataConfig['status'] = False

    def getConfig(self):
        return self.dataConfig

    def showConfig(self):
        print self.dataConfig
    
if __name__ == '__main__':
    obj = readConfig('/home/tdc/Documents/ftrace/5_autotest/script/z_config')
    obj.showConfig()
