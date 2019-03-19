#! /bin/bash

FTRACE_ON=false
LogFolderPath=/home/tdc/Documents/ftrace/5_autotest/log/$4
FolderPath=/home/tdc/Documents/ftrace/5_autotest
round=$1
target=$2

# Check input arguments
if [ $# -ne 4 ]
  then
    echo "Please make sure the arguements appended as below ./pid_trace round device pageSize timeStamp"
    echo "Please make sure the swap partitions have been mounted as swap disks"
    echo "EX: ./pid_trace.sh 1 sdb 10240 20180101_120000 True"
    exit 1
fi

re='^[0-9]+$'
if ! [[ $3 =~ $re ]] && ! [[ $1 =~ $re ]] ; then
    echo "error: Not a number"  
    exit 1
fi

i=$1_$2_$3
FTRACE_ON=$5

echo 0 > /proc/sys/vm/page-cluster
# kengyu: echo 100 > /proc/sys/vm/swappiness
echo 0 > /proc/sys/vm/swappiness
sync

### Config swappiness setting
echo "Config swappiness setting"
echo "Set swappiness and page-cluster" > $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
echo "echo 0 > /proc/sys/vm/page-cluster" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
echo "echo 100 > /proc/sys/vm/swappiness" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log

### Input a series of functions in filter 
if [ "$FTRACE_ON" == "True" ]; then
    echo "Input a series of functions in filter"
    echo 1048576 > /sys/kernel/debug/tracing/buffer_size_kb
    cat $FolderPath/script/z_filter_function > /sys/kernel/debug/tracing/set_ftrace_filter
    echo function_graph > /sys/kernel/debug/tracing/current_tracer
fi

### Start tracing
echo "Start tracing"
### Record meminfo
echo "cat /proc/meminfo:" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
cat /proc/meminfo >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log

if [ "$FTRACE_ON" == "True" ]; then
    echo "/usr/bin/time -v $FolderPath/code/paging_w $3" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
    echo 1 > /sys/kernel/debug/tracing/tracing_on
    /usr/bin/time -v $FolderPath/code/paging_w $3 &>> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log & PID=$(pgrep --parent "$!")

    echo "Paging_w PID is $PID, kswapd PID is $(pgrep kswapd0)"
    echo $(pgrep kswapd0) >> /sys/kernel/debug/tracing/set_ftrace_pid
    echo "$PID" >> /sys/kernel/debug/tracing/set_ftrace_pid
else
    /usr/bin/time -v $FolderPath/code/paging_w $3 &>> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log & PID=$(pgrep --parent "$!")
    echo "Paging_w PID is $PID, kswapd PID is $(pgrep kswapd0)"
fi

### If this script is killed, kill the 'paging_w'.
echo "" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log

trap "kill $PID 2> /dev/null" EXIT
while kill -0 $PID 2> /dev/null; do
    date -R >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
    vmstat >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
    echo >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
    sleep 1
done
trap - EXIT

echo "cat /proc/meminfo" >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log
cat /proc/meminfo >> $LogFolderPath/meminfo/pid_trace_meminfo_$i.log

if [ "$FTRACE_ON" == "True" ]; then
    ### Stop tracing
    echo 0 > /sys/kernel/debug/tracing/tracing_on

    ### Setup logs options
    echo funcgraph-proc > /sys/kernel/debug/tracing/trace_options
    cp -f /sys/kernel/debug/tracing/trace $LogFolderPath/ftrace/pid_trace_$i.log

    ### Record tracing time
    echo 1 > /sys/kernel/debug/tracing/options/sleep-time
    echo 1 > /sys/kernel/debug/tracing/options/graph-time


    ### Clean tracing config
    echo nop > /sys/kernel/debug/tracing/current_tracer

    echo 0 > /sys/kernel/debug/tracing/trace
    echo "" > /sys/kernel/debug/tracing/set_ftrace_pid

    echo "" > /sys/kernel/debug/tracing/set_ftrace_filter
    echo "" > /sys/kernel/debug/tracing/set_graph_function


    echo "" > /sys/kernel/debug/tracing/set_event
    echo "" > /sys/kernel/debug/tracing/set_event_pid

    python $FolderPath/script/ftd $LogFolderPath/ftrace/pid_trace_$i.log > $LogFolderPath/ftd/pid_trace_ftd_$i.log
fi

exit 0


