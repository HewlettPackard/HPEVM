#!/usr/bin/env python

import argparse
import subprocess
import os

class swapDevMount:
    def __init__(self, dev, devInfo='192.168.0.1,iqn.2017-04.tdc.hpe,3260,1'):
        # devInfo is a string with seperate mark ",:"
        # devInfo will transform to the format [[],[],[],...]
        self.completed = True
        if dev == "RDMA":
            # The devInfo string for RDMA should like this IP,TName,TPort,TLUM:IP,TName,TPort,TLUM:
            # For devInfo of RDMA format is [[IP,TargetName,TargetPort,TargetLUM],[],...]
            # In here, since we only have one RDMA LUM, we directly assign value inside
            self.devInfo = devInfo.split(':')
            for rdma in self.devInfo:
                rdma = rdma.split(',')
                os.system('modprobe ib_iser')
                os.system('iscsiadm -m discovery -t st -p ' + rdma[0])
                os.system('iscsiadm -m node -T ' + rdma[1] +' -o update -n iface.transport_name -v iser')
                os.system('iscsiadm -m node -T ' + rdma[1] + ' --portal ' + rdma[0]+':'+rdma[2]+','+rdma[3] + ' --login')

            pro = subprocess.Popen(['iscsiadm','-m','session','-P','3'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, errors = pro.communicate()
            self.dev = ''

            for line in output.splitlines():
                if 'Attached scsi disk' in line:
                    if self.dev == '':
                        self.dev = line.split()[3]
                    else:
                        self.dev += ','+line.split()[3]
            print 'RDMA block device mounted at ' + self.dev

            if self.mountDev():
                print "Complete mount RDMA(s) " + self.dev + " as swap partition(s)"
            else:
                self.completed = False
                print "One of the block devices does not exist!! Please check"
            
        elif dev == "RAM":
            self.dev = dev
        else:
            print "Start Mount Disk(s) as swap partition(s)"
            self.dev = dev
            if self.mountDev():
                print "Complete Mount Disk(s) " + self.dev + " as swap partition(s)"
            else:
                self.completed = False
                print "One of the block devices does not exist!! Please check" 
     
    def mountDev(self):
        for swap in self.dev.split(','):
            if os.path.exists('/dev/'+swap):
                os.system('mkswap /dev/'+swap)               
                os.system('swapon /dev/'+swap)
            else:
                return False
        return True

    def getDev(self):
        return self.dev
if __name__ == "__main__":
    pass  
