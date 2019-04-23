#!/bin/bash


if [ "$#" -eq 1 ]; then
    MEMPOOLSIZE=$1
elif [ "$#" -eq 0 ]; then
    MEMPOOLSIZE="500G"
else
    echo "Not a valid input"
    exit
fi

echo "The size of ramdisk image is" $MEMPOOLSIZE
		
tgtadm --lld iser --op delete --mode logicalunit --tid 1 --lun 1
systemctl stop tgt.service
rm /mnt/ramdisk/mempool.img
mount -t tmpfs -o size=$MEMPOOLSIZE tmpfs /mnt/ramdisk
fallocate -l $MEMPOOLSIZE /mnt/ramdisk/mempool.img
systemctl start tgt.service
tgtadm --lld iser --op new --mode target --tid 1 -T iqn.2017-04.tdc.hpe
tgtadm --lld iser --op bind --mode target --tid 1 -I ALL
tgtadm --lld iser --op new --mode logicalunit --tid 1 --lun 1 --backing-store /mnt/ramdisk/mempool.img --blocksize=4096
