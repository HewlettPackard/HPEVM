#!/bin/bash
# git clone https://github.com/spdk/spdk to $HOME/github/


spdk_root=/home/tdc/github/spdk
rdma_pci_id=0000:11:00.0 # 'lspci |grep Mellanox'
rdma_ip=192.168.0.27
nqn=nqn.2016-06.io.spdk:cnode1

pushd $spdk_root
# ref: https://spdk.io/doc/bdev.html
sudo scripts/rpc.py nvmf_create_transport -t RDMA -u 8192 -p 4 -c 0
sudo scripts/rpc.py bdev_nvme_attach_controller -b NVMe1 -t PCIe -a $rdma_pci_id
sudo scripts/rpc.py nvmf_create_subsystem $nqn -a -s SPDK00000000000001 -d NVMe1n1
sudo scripts/rpc.py nvmf_subsystem_add_ns $nqn NVMe1n1
sudo scripts/rpc.py nvmf_subsystem_add_listener $nqn -t rdma -a $rdma_ip -s 4420
popd
