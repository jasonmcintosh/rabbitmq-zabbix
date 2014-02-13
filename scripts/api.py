#!/usr/bin/env /usr/bin/python
'''Python module to query the RabbitMQ Management Plugin REST API and get
results that can then be used by Zabbix.'''
import json
import optparse
import socket
import time
import urllib2
import subprocess
import os

class RabbitMQAPI(object):
    '''Class for RabbitMQ Management API'''
    queueOptions=["memory","messages","messages_unacknowledged","consumers"]

    def __init__(self, user_name='guest', password='guest', host_name='',
                 port=15672):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name or socket.gethostname()
        self.port = port

    def call_api(self, path):
        '''Call the REST API and convert the results into JSON.'''
        url = 'http://{0}:{1}/api/{2}'.format(self.host_name, self.port, path)
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.user_name, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        return json.loads(urllib2.build_opener(handler).open(url).read())

    def list_queues(self, filters=None):
        '''
        List all of the RabbitMQ queues. "filters" is an optional
        parameter that is a dictionary of key-value pairs to match against to
        filter down the queue to only those that are desired.
        '''
        queues = []
        for queue in self.call_api('queues'):
            element = {'{#VHOSTNAME}': queue['vhost'],
                       '{#QUEUENAME}': queue['name']}
            if filters:
                ## Check each filter element against the current queue and only
                ## there are any mismatches, don't add that queue.
                if not [x for x in filters if filters[x] != queue.get(x)]:
                    queues.append(element)
            else:
                queues.append(element)
        return queues

    def list_nodes(self):
        '''List all the RabbitMQ nodes.'''
        return [x['name'] for x in self.call_api('nodes')]

    def check_queue(self):
	returnCode = 0
        '''Return the value for a specific item in a queue's details.'''
        data = self.call_api('queues')
	for queueData in data:
		for itemData in self.queueOptions:
			zabbixKey="\"rabbitmq["+queueData['vhost']+",queue_"+itemData+","+queueData['name']+"]\""
			if queueData.get(itemData):
				zabbixValue=queueData[itemData]
			else:
				zabbixValue=0
			with open(os.devnull, 'w') as devnull:
				returnCode |=subprocess.call('zabbix_sender -c /etc/zabbix/zabbix_agentd.conf -k '+zabbixKey + ' -o ' + str(zabbixValue), shell=True, stdout=devnull, stderr=devnull)
			#print 'Response of ' + str(returnCode) + ' zabbix_sender -c /etc/zabbix/zabbix_agentd.conf -k '+zabbixKey + ' -o ' + str(zabbixValue)
	return returnCode
    def check_aliveness(self):
        '''Check the aliveness status of a given vhost.'''
        return self.call_api('aliveness-test/%2f')['status']

    def check_server(self, item, node_name=None):
        '''Return the value for a specific item in a node's details.'''
        if not node_name:
            node_name = 'rabbit@{0}'.format(self.host_name)
        return self.call_api('nodes/{0}'.format(node_name)).get(item)


def main():
    '''Command-line parameters and decoding for Zabbix use/consumption.'''
    parser = optparse.OptionParser()
    parser.add_option('--username', help='RabbitMQ API username', default='guest')
    parser.add_option('--password', help='RabbitMQ API password', default='guest')
    parser.add_option('--hostname', help='RabbitMQ API host', default=socket.gethostname())
    parser.add_option('--port', help='RabbitMQ API port', type='int', default=15672)
    parser.add_option('--check', help='Type of check - list_queues, queues server depending on what we are doing', default="")
    parser.add_option('--metric', help='Which metric to evaluate (used only for the server check)', default="")
    parser.add_option('--filters', help='Filter to restrict which queues are shown', default="")
    (options, args) = parser.parse_args()
    api = RabbitMQAPI(user_name=options.username, password=options.password,
                      host_name=options.hostname, port=options.port)
    if options.check == 'list_queues':
        if options.filters:
            try:
                filters = json.loads(options.filters)
            except KeyError:
                parser.error('Invalid filters object.')
        else:
            filters = {}
        print json.dumps({'data': api.list_queues(filters)})
    elif options.check == 'list_nodes':
        print json.dumps({'data': api.list_nodes()})
    elif options.check == 'queues':
        print api.check_queue()
    elif options.check == 'check_aliveness':
        print api.check_aliveness()
    elif options.check == 'server':
        if not options.metric:
            message = 'Required parameter: "metric" when checking server state '
            parser.error(message)
        else:
            print api.check_server(options.metric)

if __name__ == '__main__':
    main()
