modprobe ib_iser
iscsiadm -m discovery -t st -p 192.168.0.1
iscsiadm -m node -T iqn.2017-04.tdc.hpe -o update -n iface.transport_name -v iser
iscsiadm -m node -T iqn.2017-04.tdc.hpe | grep transport
iscsiadm -m node -T iqn.2017-04.tdc.hpe --portal 192.168.0.1:3260,1 --login
iscsiadm -m session -P 3
