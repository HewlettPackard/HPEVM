#!/usr/bin/env python
# (c) Copyright [2019] Hewlett Packard Enterprise Development LP
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License, version 2, as
# published by the Free Software Foundation; either version 2 of the
# License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# Rev 1.0 03/04/2019
#

import subprocess
import os
import sys
import re

class swapDevManager:
    def __init__(self, ip, name, action='login' , dev='RDMA',  wwn='iqn.2017-04.tdc.hpe' ):
        self.completed = True
        self.getMountDev();        

        if dev == 'RDMA' and action == 'login':
            os.system('modprobe ib_iser')
            os.system('iscsiadm -m discovery -t st -p ' + ip)
            os.system('iscsiadm -m node -T ' + wwn +' -o update -n iface.transport_name -v iser')
            os.system('iscsiadm -m node -l -T ' + wwn + ':' + name + ' -p ' + ip + ':3260')

            pro = subprocess.Popen(['iscsiadm','-m','session','-P','3'],
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, errors = pro.communicate()
            self.dev = ''

            for line in output.splitlines():
                if 'Attached scsi disk' in line:
                    if self.dev == '':
                        self.dev = line.split()[3]
                    else:
                        self.dev += ','+line.split()[3]
            # print 'RDMA block device mounted at ' + self.dev

            if self.mountDev():
                print "Complete mount RDMA(s) " + self.dev + " as swap partition(s)"
            else:
                self.completed = False
                print "One of the block devices does not exist!! Please check"
        
        elif action == 'logout':
            if os.path.exists('/dev/'+dev):
                os.system('swapoff /dev/' + dev)
                os.system('iscsiadm -m node -u -T ' +  wwn + ':' + name + ' -p ' + ip + ':3260')
            else:
                print('Error: The input block device not found')

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
        flag = True
        for swap in self.dev.split(','):
            if os.path.exists('/dev/'+swap):
                if '/dev/'+swap not in self.mountedDev:
                    print('Info: Mount the RDMA remote memory on ' + swap)
                    os.system('mkswap /dev/'+swap)               
                    os.system('swapon /dev/'+swap)
            else:
                flag = False
        return flag

    def getDev(self):
        return self.dev

    def getMountDev(self):
        pro = subprocess.Popen(['swapon','-s'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, errors = pro.communicate()
        self.mountedDev = []

        for line in output.splitlines():
            if '/dev/' in line:
                self.mountedDev.append(line.split()[0])
    
        print('mountDev:' + str(self.mountedDev ))       

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) !=5 :
        print('Please fallow the format as following show: python swapDevManager.py ip iscsiName action dev')
        print('EX: python logInOutRDMA.py 192.168.0.100 test1 login')
        print('EX: python logInOutRDMA.py 192.168.0.100 test1 logout sdc')

    else:
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",sys.argv[1]):
            if sys.argv[3] == 'login':
                swapDevManager(sys.argv[1],sys.argv[2])
            elif sys.argv[3] == 'logout' and len(sys.argv)==5:
                swapDevManager(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
            else:
                print('Error: Please check the inpur format is correct')
        else:
            print('ERROR: IP are not match')

