To use this script, first build with:

'docker build --tag log-sender .'

Then set the following environment variables:

export LOGS_DIR="/home/csroot/drain/logs"
export PROT=tcp
export DST=10.12.2.150:5140
export TAG=tag
export MESSAGES_PER_SECOND=1000


sudo docker run -v $LOGS_DIR:/app/mounted_logs --log-driver syslog --log-opt syslog-address=$PROT://$DST --log-opt syslog-format=rfc5424  --log-opt tag=$TAG -e messages_per_second=$MESSAGES_PER_SECOND -d log-sender
