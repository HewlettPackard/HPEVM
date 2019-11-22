#!/bin/bash
pagingW="/home/tdc/github/HPEVM/microbenchmark/code/paging_w"
sizeGB=$1
iter=$2
exp="0"
logPath="/home/tdc/hpevm/log/pagingw"
iscsiClientBin="/home/tdc/hpevm/scripts/iscsi_client_login_server.sh"
if ! test -d $logPath; then
	mkdir -p $logPath
fi

#TODO: link '${dev} with protocol/device/swap on/off functions
#dev="pcieNvme"
#dev="pmem"
#dev="fullram"
#dev="ssd"
dev="remoteNvmeSpdk"

# -- protocol/device/swap on/off functions --
# local PCIe NVMe
pcie_nvme()
{
	_swapCtrl $1 "/dev/nvme0n1"
}

# local pmem
pmem()
{
	_swapCtrl $1 "/dev/pmem0"
}

# local SATA drive
ssd()
{
	_swapCtrl $1 "/dev/sda"
}

# local SAS drive
sas()
{
	_swapCtrl $1 "/dev/sde"
}

# remote PCIe-NVMe with TGT
remote_nvme()
{
	local on=$1
	if test "$on" = "on"; then
		sudo $iscsiClientBin 1
		_swapCtrl $1 "/dev/sdc"
	else
		_swapCtrl $1 "/dev/sdc"
		sudo $iscsiClientBin 0
	fi
}

# remote PCIe-NVMe with SPDK 
remote_nvme_spdk()
{
	local on=$1
	local dev="/dev/nvme0n1"
	if test "$on" = "on"; then
		sudo nvme connect -t rdma -n "nqn.2016-06.io.spdk:cnode1" -a 192.168.0.27 -s 4420
		_swapCtrl $on $dev
	else
		_swapCtrl $on $dev
		sudo nvme disconnect -n "nqn.2016-06.io.spdk:cnode1"
	fi
}

# common swap on/off function
_swapCtrl()
{
	local on=$1
	local media=$2

	#echo "swap${on} $media"

	if test "$on" = "on"; then
		sudo mkswap $media > /dev/null 2>&1
		sudo swapon $media > /dev/null 2>&1
	else
		sudo swapoff $media > /dev/null 2>&1
	fi
}

if [[ -z $sizeGB ]]; then
    sizeGB=1
fi

if [[ -z $iter ]]; then
    iter=10
fi


pagingWLog="$logPath/${dev}_pagingW_${sizeGB}G_$(date +%Y%m%d_%H%M%S).log"
vmstatLog="$logPath/${dev}_vmstat_${sizeGB}G_$(date +%Y%m%d_%H%M%S).log"
freeLog="$logPath/${dev}_free_${sizeGB}G_$(date +%Y%m%d_%H%M%S).log"

echo "Run $0 $sizeGB GB for $iter times" 2>&1 | tee -a $pagingWLog
free -h -w -s 1 2>&1 > $freeLog &
pidFree=$!
vmstat -w -t 1 2>&1 > $vmstatLog &
pidVmstat=$!

for i in $(seq 1 1 $iter)
do
    #TODO: link '${dev} with protocol/device/swap on/off functions
    #pcie_nvme "on"
    #pmem "on"
    #ssd "on"
    #sas "on"
    #remote_nvme "on"
    remote_nvme_spdk "on"
    t=$(/usr/bin/time -p $pagingW $(($sizeGB*1024)) 2>&1 | tee -a ./time.log | grep real |cut -d ' ' -f 2)
    echo "[$i] paging_w $sizeGB GB cost $t seconds" | tee -a $pagingWLog
    exp=${exp}+$t
    #pcie_nvme "off"
    #pmem "off"
    #ssd "off"
    #sas "off"
    #remote_nvme "off"
    remote_nvme_spdk "off"
done

kill $pidFree > /dev/null 2>&1
kill $pidVmstat > /dev/null 2>&1

avg=$(echo "scale=3;(${exp})/$iter" | bc -l)
echo "average: $avg seconds" | tee -a $pagingWLog
