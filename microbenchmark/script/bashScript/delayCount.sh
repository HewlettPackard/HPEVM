#! /bin/bash

filePath=/home/tdc/Documents/ftrace/3_minorTest/script/0_log/
fileDisk=/home/tdc/Documents/ftrace/3_minorTest/script/0_log/z_disk.log
fileRDMA=/home/tdc/Documents/ftrace/3_minorTest/script/0_log/z_rdma.log
delay="+!#*@$"
init=10

echo $delay > $fileDisk
echo $delay > $fileRDMA

for i in {1..13}
do
	echo "pid_trace_${init}_1.log" >> $fileDisk
        echo "pid_trace_${init}_2.log" >> $fileRDMA
	
	cat z_ftdHeader > ${filePath}pid_trace_ftd_delay_${init}_1.log 
        cat z_ftdHeader > ${filePath}pid_trace_ftd_delay_${init}_2.log

	for (( j=0; j<${#delay}; j++ ))
        do
		c=${delay:$j:1}
		echo "$c count:" >> $fileDisk
		cat ${filePath}pid_trace_${init}_1.log | grep "paging" | grep -F " $c " | grep -v " } " >> ${filePath}pid_trace_ftd_delay_${init}_1.log 
                cat ${filePath}pid_trace_${init}_1.log | grep "paging" | grep -F " $c " | grep -v " } " | wc -l >> $fileDisk
                
		echo "$c count:" >> $fileRDMA
		cat ${filePath}pid_trace_${init}_2.log | grep "paging" | grep -F " $c " | grep -v " } " >> ${filePath}pid_trace_ftd_delay_${init}_2.log
      	        cat ${filePath}pid_trace_${init}_2.log | grep "paging" | grep -F " $c " | grep -v " } " | wc -l >> $fileRDMA
	done
        ./ftd ${filePath}pid_trace_ftd_delay_${init}_1.log >> $fileDisk
        ./ftd ${filePath}pid_trace_ftd_delay_${init}_2.log >> $fileRDMA
	init=$((init*2))
 
done
exit 0
