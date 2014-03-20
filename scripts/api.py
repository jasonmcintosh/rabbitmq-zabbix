#!/usr/bin/env /usr/bin/python
'''Python module to query the RabbitMQ Management Plugin REST API and get
results that can then be used by Zabbix.'''
import json
import optparse
import socket
import urllib2
import subprocess


class RabbitMQAPI(object):
    '''Class for RabbitMQ Management API'''

    def __init__(self, user_name='guest', password='guest', host_name='',
                 port=15672, conf='/etc/zabbix/zabbix_agentd.conf'):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name or socket.gethostname()
        self.port = port
        self.conf = conf

    def call_api(self, path):
        '''Call the REST API and convert the results into JSON.'''
        url = 'http://{0}:{1}/api/{2}'.format(self.host_name, self.port, path)
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.user_name, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        return json.loads(urllib2.build_opener(handler).open(url).read())

    def list_queues(self, filters=None):
        '''
        List all of the RabbitMQ queues, filtered against the filters provided
        in .rab.auth. See README.md for more information.
        '''
        queues = []
        if not filters:
            filters = [{}]
        for queue in self.call_api('queues'):
            for _filter in filters:
                check = [(x, y) for x, y in queue.items() if x in _filter]
                shared_items = set(_filter.items()).intersection(check)
                if len(shared_items) == len(_filter):
                    element = {'{#VHOSTNAME}': queue['vhost'],
                               '{#QUEUENAME}': queue['name']}
                    queues.append(element)
                    break
        return queues

    def check_queue(self, filters=None):
        '''Return the value for a specific item in a queue's details.'''
        return_code = 0
        if not filters:
            filters = [{}]
        for queue in self.call_api('queues'):
            success = False
            for _filter in filters:
                check = [(x, y) for x, y in queue.items() if x in _filter]
                shared_items = set(_filter.items()).intersection(check)
                if len(shared_items) == len(_filter):
                    success = True
                    break
            if success:
                return_code |= self._send_data(queue)
        return return_code

    def _send_data(self, queue):
        '''Send the queue data to Zabbix.'''
        args = 'zabbix_sender -c {0} -k {1} -o {2}'
        for item in ['memory', 'messages', 'messages_unacknowledged', 'consumers']:
            key = '"rabbitmq[{0},queue_{1},{2}]"'
            key = key.format(queue['vhost'], item, queue['name'])
            value = queue.get(item, 0)
	    #print "Executing ", args.format(self.conf, key, value)
        return subprocess.call(args.format(self.conf, key, value), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #return 0

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
    choices = ['list_queues', 'queues', 'check_aliveness', 'server']
    parser = optparse.OptionParser()
    parser.add_option('--username', help='RabbitMQ API username',
                      default='guest')
    parser.add_option('--password', help='RabbitMQ API password',
                      default='guest')
    parser.add_option('--hostname', help='RabbitMQ API host',
                      default=socket.gethostname())
    parser.add_option('--port', help='RabbitMQ API port', type='int',
                      default=15672)
    parser.add_option('--check', type='choice', choices=choices,
                      help='Type of check')
    parser.add_option('--metric', help='Which metric to evaluate', default='')
    parser.add_option('--filters', help='Filter used queues (see README)')
    parser.add_option('--conf', default='/etc/zabbix/zabbix_agentd.conf')
    (options, args) = parser.parse_args()
    if not options.check:
        parser.error('At least one check should be specified')
    api = RabbitMQAPI(user_name=options.username, password=options.password,
                      host_name=options.hostname, port=options.port,
                      conf=options.conf)
    if options.filters:
        try:
            filters = json.loads(options.filters)
        except KeyError:
            parser.error('Invalid filters object.')
    else:
        filters = [{}]
    if not isinstance(filters, (list, tuple)):
        filters = [filters]
    if options.check == 'list_queues':
        print json.dumps({'data': api.list_queues(filters)})
    elif options.check == 'queues':
        print api.check_queue(filters)
    elif options.check == 'check_aliveness':
        print api.check_aliveness()
    elif options.check == 'server':
        if not options.metric:
            parser.error('Missing required parameter: "metric"')
        else:
            print api.check_server(options.metric)

if __name__ == '__main__':
    main()
