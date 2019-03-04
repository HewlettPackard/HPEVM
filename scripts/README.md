# Scripts for setup iSCSI ramdisk backstore with iSER enabled

## Script Description
logInOutRDMA.py		- login/logout remote iSCSI target. Also activates or deactivates the swap device atop it.
swapDevManager.py	- creates/deletes iSCSI ramdisk backstore on memory provider.

## Script Usage:

### On the memory provider node:

#### Creates ramdisk backstore:

swapDevManager.py server_ip name size create

#### Delete ramdisk backstore:

swapDevManager.py server_ip name delete

##### Example - create a iSCSI ramdisk backstore of 10 MB on server 192.168.0.1 with 'test1' as the name

./swapDevManager.py 192.168.0.100 test1 10 create

##### Example - delete the iSCSI ramdisk backstore named 'test1'

./swapDevManager.py 192.168.0.100 test1 delete

### On the memory user node:

#### Login remote iSCSI target and create a local swap device:

logInOutRDMA.py server_ip name login

#### Logout remote iSCSI target and delete the local swap device:

logInOutRDMA.py server_ip name logout dev_name

##### Example - login and activate local swap device that connects to the remote iSCSI target

./logInOutRDMA.py 192.168.0.100 test1 login

##### Example - logout remote iSCSI target and deactivate the swap device (/dev/sdc)

./logInOutRDMA.py 192.168.0.100 test1 logout sdc
