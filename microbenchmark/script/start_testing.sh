#! /bin/bash

systemctl enable autoGenPagingLog.service

echo "WARMING!!! System will reboot after 10 SECs !!!"
echo "Please make sure the configurations are set !!!"
echo "For test config: modify z_config !!!"  
echo "For tracing specific function: modify z_filter_function !!!" 
echo "For sent out notification: z_mailList !!!" 
echo "For mulitple mail accounts, use ',' with one line only. EX: a@a.com,b@b.com"
sleep 10
reboot
