#!/bin/bash

#portal=$1
#target_name=$2
#login=1

fail()
{
    echo -e "\n$1\n"
    exit 1
}

logIn()
{
    local portal=$1
    local target_name=$2

    if test -z $portal; then
        portal="192.168.0.1:3260"
    fi

    # iSCSI's naming convention to node name: IQN(iSCSI Qualified Name) format
    # iqn.yyyy-mm.naming-authority:unique name
    if test -z $target_name; then
        target_name="iqn.2017-04.tdc.hpe"
    fi

    # Check for existing session first
    iscsiadm -m session | grep ${portal}.*${target_name} && echo "session exist" && exit 0

    modprobe ib_iser

    # discover iSCSI target with server portal (ip[:port=default 3260]) and type 'st'(SendTarget?)
    iscsiadm -m discovery -t st -p ${portal} || fail "[err] Failed to discover iSCSI target at ${portal}"

    # Enable 'iser' by updating 'iface.transport_name' field of open-iscsi db record
    iscsiadm -m node -T ${target_name} -o update -n iface.transport_name -v iser ||\
        fail "[err] Failed to enable iser with target name: ${target_name}"

    # Verify transport name
    transport=$(iscsiadm -m node -T ${target_name} | grep 'iface.transport_name' | cut -d ' ' -f 3)
    if test -z ${transport} -o ! ${transport} = "iser"; then  
        fail "[err] iser is not set"
    fi

    # login target
    iscsiadm -m node -T ${target_name} --portal ${portal},1 --login 
    echo "Successfully login node target \"${target_name}\" on \"${portal}\""

    # there should be a new iscsi block device created after login (e.g. /dev/sdc)
    ls /dev/sd*
}

showSession()
{
    iscsiadm -m session
}

logOut()
{
    local portal=$1
    local target_name=$2
    if [[ ! -z "$portal" && ! -z "$target_name" ]] ; then
        echo "logOut"
        iscsiadm -m node -T ${target_name} --portal ${portal},1 --logout
    fi
}

#TODO: make 'portal' and 'login' as variables if needed
login=$1
portal=192.168.0.27:3260
target="iqn.2017-04.tdc.hpe:1"

#portal=$1
#target=$2
#login=$3
if [[ $login -eq 1 ]] ; then
    logIn $portal $target 
else
    logOut $portal $target
fi

