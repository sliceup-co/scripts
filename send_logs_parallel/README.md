To use this script, first build with:

'docker build --tag log-sender .'

Then set the following environment variables:

export LOGS_DIR="/home/csroot/drain/logs"
export PROT=udp
export DST=10.12.2.90:514
export TAG=tag
export MESSAGES_PER_SECOND=2000


sudo docker run -v $LOGS_DIR:/app/mounted_logs --log-driver syslog --log-opt syslog-address=$PROT://$DST --log-opt syslog-format=rfc5424  --log-opt tag=$TAG -e messages_per_second=$MESSAGES_PER_SECOND -d log-sender
