# HPEVM - High Performance and Extensible Virtual Memory

This repository contains scripts that HPE developed for the HPEVM technology.

scripts/    - scripts for setup iSCSI ramdisk backstore with iSER enabled, both on client and server side.

## Environment Settings

### Hardware

Machine Model: HPE DL360 Gen10
CPU: Intel XEON Gold 6128 @ 3.40 GHz
NIC: HPE 640FLR_SFP28 PCIe cards (25 G/s)

### Software

Operating System: Red Hat Enterprise Linux 7.4
RDMA NIC Driver: Mellonex OFED Driver 4.2-1.2.0.0 (MLNX_OFED_LINUX-4.2-1.2.0.0-rhel7.4-x86.64)

* Note: The scripts has been tested on Red Hat Enterprise Linux (RHEL 7.4). Although not yet tested, we think CentOS 7.4 should work as well.
