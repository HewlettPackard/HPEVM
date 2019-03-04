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

import sys
import os
import subprocess
import socket
import re

class swapDevManager:
    def __init__(self, ip, name, size, action, sizeScale='G', wwn='iqn.2017-04.tdc.hpe'):
        self.ip = ip
        self.wwn = wwn
        self.name = name
        self.size = size
        self.sizeScale = sizeScale
        self.wwn = wwn        

        if action == 'create':
            if self.create():
                print('Success to Create iSCSI name ' + name + ' with size ' + size)
            else:
                print('Error in Create Operation')            
        elif action == 'delete':
            if self.delete():
                 print('Success to delete iSCSI name ' + name )
            else:
                print('Error in Delete Operation')
        else:
            print('Invalid action!!!')

    def create(self):
        pro = subprocess.Popen(['targetcli','backstores/ramdisk', 'create','name='+self.name,'size='+self.size+self.sizeScale]
                               ,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, errors = pro.communicate()
    
        for line in errors.splitlines():
            if 'exists' in line:
                print('Error: Storage object ramdisk exists')
                return False

        wwnName = self.wwn + ':' + self.name
        os.system('targetcli iscsi/ create wwn=' + wwnName)
        os.system('targetcli iscsi/' + wwnName + '/tpg1/luns create lun=0 storage_object=/backstores/ramdisk/' + self.name)
        os.system('targetcli iscsi/' + wwnName + '/tpg1/portals delete 0.0.0.0 3260')
        os.system('targetcli iscsi/' + wwnName + '/tpg1/portals create ' + self.ip  + ' 3260')
        os.system('targetcli iscsi/' + wwnName + '/tpg1/portals/' + self.ip  + ':3260 enable_iser boolean=true')
        os.system('targetcli iscsi/' + wwnName + '/tpg1 set attribute authentication=0 demo_mode_write_protect=0 generate_node_acls=1 cache_dynamic_acls=1')
        os.system('targetcli saveconfig')
        return True

    def delete(self):
        wwnName = self.wwn + ':' + self.name
        if self.name == "ALLCONFIGNEEDTOCLEAN":
            os.system('targetcli clearconfig confirm=True')
        else:
            pro = subprocess.Popen(['targetcli','iscsi/', 'delete', wwnName],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, errors = pro.communicate()
            
            for line in errors.splitlines():
                if 'No such' in line:
                    print('Error: No such Target in configfs ' + self.name)
                    return False

            os.system('targetcli backstores/ramdisk delete ' + self.name)
            os.system('targetcli saveconfig')
        return True

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Please fallow the format as following show:')
        print('\tpython swapDevManager.py IP ISCSINAME RANDISKSIZE(GiB) create')
        print('\tpython swapDevManager.py IP ISCSINAME delete')
        print('EX: python swapDevManager.py 192.168.0.100 test1 10 create')
        print('EX: python swapDevManager.py 192.168.0.100 test1 delete')

    else:
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",sys.argv[1]):
            if sys.argv[3] == 'delete':
                swapDevManager(sys.argv[1],sys.argv[2],0,sys.argv[3])
            elif sys.argv[4] == 'create' and sys.argv[3].isdigit() and int(sys.argv[3]) < 501:
                swapDevManager(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
            else:
                print('Error: ramDiskSize is too large. Enter number less than 500')
        else:
            print('ERROR: IP are not match')
    
