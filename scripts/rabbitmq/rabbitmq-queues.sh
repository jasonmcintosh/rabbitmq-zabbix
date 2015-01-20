cd "$(dirname "$0")"

. .rab.auth

METRIC=$2
NODE=$3

if [[ -z "$HOSTNAME" ]]; then
    HOSTNAME=`hostname`
fi
if [[ -z "$NODE" ]]; then
    NODE=`hostname`
fi
#rabbitmq[queues]
#rabbitmq[server,disk_free]

# This assumes that the server is going to then use zabbix_sender to feed the data BACK to the server.  Right now, I'm doing that
# in the python script

./api.py --hostname=$HOSTNAME --username=$USERNAME --password=$PASSWORD --check=queues --metric=$METRIC --node="$NODE" --filters="$FILTER" --conf=$CONF
