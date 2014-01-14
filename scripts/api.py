#!/usr/bin/env /usr/bin/python
'''Python module to query the RabbitMQ Management Plugin REST API and get
results that can then be used by Zabbix.'''
import json
import optparse
import socket
import time
import urllib2


class RabbitMQAPI(object):
    '''Class for RabbitMQ Management API'''

    def __init__(self, user_name='guest', password='guest', host_name='',
                 port=15672, vhost=''):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name or socket.gethostname()
        self.port = port
        self.vhost = vhost

    def call_api(self, path):
        '''Call the REST API and convert the results into JSON.'''
        url = 'http://{0}:{1}/api/{2}'.format(self.host_name, self.port, path)
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.user_name, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        return json.loads(urllib2.build_opener(handler).open(url).read())

    def list_queues(self, filters=None):
        '''
        List all of the RabbitMQ queues. If vhost has been passed to the class,
        it will only look at queues on that vhost. "filters" is an optional
        parameter that is a dictionary of key-value pairs to match against to
        filter down the queue to only those that are desired.
        '''
        queues = []
        path = 'queues/{0}'.format(self.vhost) if self.vhost else 'queues'
        for queue in self.call_api(path):
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

    def check_queue(self, queue, item):
        '''Return the value for a specific item in a queue's details.'''
        vhost = self.vhost if self.vhost else '%2F'
        data = self.call_api('queues/{0}/{1}'.format(vhost, queue))
        if item == 'idle_since':
            struct_time = time.strptime(data[item], '%Y-%m-%m %H:%M:%S')
            return int(time.mktime(struct_time))
        else:
            return data.get(item)

    def check_aliveness(self):
        '''Check the aliveness status of a given vhost.'''
        vhost = self.vhost if self.vhost else '%2F'
        return self.call_api('aliveness-test/{0}'.format(vhost))['status']

    def check_server(self, item, node_name=None):
        '''Return the value for a specific item in a node's details.'''
        if not node_name:
            node_name = 'rabbit@{0}'.format(self.host_name)
        return self.call_api('nodes/{0}'.format(node_name)).get(item)


def main():
    '''Command-line parameters and decoding for Zabbix use/consumption.'''
    parser = optparse.OptionParser()
    parser.add_option('--username', help='RabbitMQ API username',
                      default='guest')
    parser.add_option('--password', help='RabbitMQ API password',
                      default='guest')
    parser.add_option('--hostname', help='RabbitMQ API host',
                      default=socket.gethostname())
    parser.add_option('--port', help='RabbitMQ API port', type='int',
                      default=15672)
    parser.add_option('--vhost', help='RabbitMQ API virtual host')
    (options, args) = parser.parse_args()
    api = RabbitMQAPI(user_name=options.username, password=options.password,
                      host_name=options.hostname, port=options.port,
                      vhost=options.vhost)
    if not args:
        message = 'A command must be provided. Available commands: '
        message += 'list_queues, list_nodes, check_queue, check_aliveness, or '
        message += 'check_server'
        parser.error(message)
    if args[0] == 'list_queues':
        if len(args) == 2 and args[1]:
            try:
                filters = json.loads(args[1])
            except KeyError:
                parser.error('Invalid filters object.')
        else:
            filters = {}
        print json.dumps({'data': api.list_queues(filters)})
    if args[0] == 'list_nodes':
        print json.dumps({'data': api.list_nodes()})
    elif args[0] == 'check_queue':
        if len(args) != 3:
            message = 'Incorrect number of parameters for check_queue. '
            message += 'Required positional parameters: "queue" and "item"'
            parser.error(message)
        print api.check_queue(args[1], args[2])
    elif args[0] == 'check_aliveness':
        print api.check_aliveness()
    elif args[0] == 'check_server':
        if len(args) not in (2, 3):
            message = 'Incorrect number of parameters for check_server. '
            message += 'Required positional parameter: "item". '
            message += 'Optional positional parameter: "node_name".'
            parser.error(message)
        if len(args) == 2:
            print api.check_server(args[1])
        else:
            print api.check_server(args[1], args[2])


if __name__ == '__main__':
    main()
