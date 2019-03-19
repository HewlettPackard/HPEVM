Prerequisites for running the service

1. Modify the test configuration in script/z_config, especially the folder path. 
2. Modify the tracing funtions in script/z_filter_function if you need to use ftrace.
3. Modify the the log and folder path in script/pid_trace.sh
4. Compile the source code in code.
5. Execute the script/pid_trace.sh EX: ./pid_trace.sh 1 sdb 1024 test Flase for sniff test. Make sure confiuguration is well.
6. Execute the script/start_testing.sh
7. Once the testing completed, all logs will locate at log.

The steps to stop testing during the iteration.
1. Disable the service: systemctl disable z_autoGenPagingLog.service
2. Stop the service: systemctl stop z_autoGenPagingLog.service
3. Remove the tmp file under script/z_autoTest.stat

Full auto run testing service with following features.
1. The script stores logs by the timestamp of service start.
2. The script creates an excel file for each round. [Need to manually execute the tool under pythonLib folder]
3. The script send out the notification.



