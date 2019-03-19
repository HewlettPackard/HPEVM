Prerequisites for running the service

1. Modify the test configuration in z_config with initial size(GB), differences(GB), end size(GB), and how many rounds.
2. Modify the tracing funtions in z_filter_function.
3. Modify the mail list for notification when all testing done.
4. Excute the start_testing.sh

Full auto run testing service with following features.
1. The script stores logs by the timestamp of service start.
2. The script creates an excel file for each round.
3. The script send out the notification with and zip attachment when testing done.



