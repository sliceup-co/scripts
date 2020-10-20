#! /bin/bash
for i in {1..350}
do
   sudo docker run -v $LOGS_DIR:/app/mounted_logs --log-driver syslog --log-opt syslog-address=$PROT://$DST --log-opt syslog-format=rfc5424 \
 --log-opt tag="app_$i" -e messages_per_second=$MESSAGES_PER_SECOND -e loop=true -d log-sender
   echo "started $i times"
done
