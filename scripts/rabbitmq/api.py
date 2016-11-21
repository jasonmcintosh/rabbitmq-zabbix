#!/usr/bin/env /usr/bin/python
'''Python module to query the RabbitMQ Management Plugin REST API and get
results that can then be used by Zabbix.
https://github.com/jasonmcintosh/rabbitmq-zabbix
'''
import json
import optparse
import socket
import urllib2
import subprocess
import tempfile
import os
import logging


class RabbitMQAPI(object):
    '''Class for RabbitMQ Management API'''

    def __init__(self, user_name='guest', password='guest', host_name='',
                 port=15672, conf='/etc/zabbix/zabbix_agentd.conf', senderhostname=None, protocol='http'):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name or socket.gethostname()
        self.port = port
        self.conf = conf or '/etc/zabbix/zabbix_agentd.conf'
        self.senderhostname = senderhostname
        self.protocol = protocol

    def call_api(self, path):
        '''Call the REST API and convert the results into JSON.'''
        url = '{0}://{1}:{2}/api/{3}'.format(self.protocol, self.host_name, self.port, path)
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.user_name, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        logging.debug('Issue a rabbit API call to get data on ' + path + " against " + self.host_name)
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
            logging.debug("Discovered queue " + queue['name'] + ", checking to see if it's filtered...")
            for _filter in filters:
                check = [(x, y) for x, y in queue.items() if x in _filter]
                shared_items = set(_filter.items()).intersection(check)
                if len(shared_items) == len(_filter):
                    element = {'{#VHOSTNAME}': queue['vhost'],
                               '{#QUEUENAME}': queue['name']}
                    queues.append(element)
                    logging.debug('Discovered queue '+queue['vhost']+'/'+queue['name'])
                    break
        return queues

    def list_shovels(self, filters=None):
        '''
        List all of the RabbitMQ shovels, filtered against the filters provided
        in .rab.auth. See README.md for more information.
        '''
        shovels = []
        if not filters:
            filters = [{}]
        try:
            for shovel in self.call_api('shovels'):
                logging.debug("Discovered shovel " + shovel['name'] + ", checking to see if it's filtered...")
                for _filter in filters:
                    check = [(x, y) for x, y in shovel.items() if x in _filter]
                    shared_items = set(_filter.items()).intersection(check)
                    if len(shared_items) == len(_filter):
                        element = {'{#VHOSTNAME}': shovel['vhost'],
                                   '{#SHOVELNAME}': shovel['name']}
                        shovels.append(element)
                        logging.debug('Discovered shovel '+shovel['vhost']+'/'+shovel['name'])
                        break
            return shovels
        except urllib2.HTTPError as err:
            if err.code == 404:
                return shovels
            else:
                raise err

    def list_nodes(self):
        '''Lists all rabbitMQ nodes in the cluster'''
        nodes = []
        for node in self.call_api('nodes'):
            # We need to return the node name, because Zabbix
            # does not support @ as an item parameter
            name = node['name'].split('@')[1]
            element = {'{#NODENAME}': name,
                       '{#NODETYPE}': node['type']}
            nodes.append(element)
            logging.debug('Discovered nodes '+name+'/'+node['type'])
        return nodes

    def check_queue(self, filters=None):
        '''Return the value for a specific item in a queue's details.'''
        return_code = 0
        if not filters:
            filters = [{}]

        rdatafile = tempfile.NamedTemporaryFile(delete=False)

        for queue in self.call_api('queues'):
            success = False
            logging.debug("Filtering out by " + str(filters))
            for _filter in filters:
                check = [(x, y) for x, y in queue.items() if x in _filter]
                shared_items = set(_filter.items()).intersection(check)
                if len(shared_items) == len(_filter):
                    success = True
                    break
            if success:
                self._prepare_data(queue, rdatafile)

        rdatafile.close()
        return_code = self._send_data(rdatafile)
        os.unlink(rdatafile.name)
        return return_code

    def check_shovel(self, filters=None):
        '''Return the value for a specific item in a shovel's details.'''
        return_code = 0
        if not filters:
            filters = [{}]

        rdatafile = tempfile.NamedTemporaryFile(delete=False)

        for shovel in self.call_api('shovels'):
            success = False
            logging.debug("Filtering out by " + str(filters))
            for _filter in filters:
                check = [(x, y) for x, y in shovel.items() if x in _filter]
                shared_items = set(_filter.items()).intersection(check)
                if len(shared_items) == len(_filter):
                    success = True
                    break
            if success:
                key = '"rabbitmq.shovels[{0},shovel_{1},{2}]"'
                key = key.format(shovel['vhost'], 'state', shovel['name'])
                value = shovel.get('state', 0)
                logging.debug("SENDER_DATA: - %s %s" % (key,value))
                rdatafile.write("- %s %s\n" % (key, value))


        rdatafile.close()
        return_code = self._send_data(rdatafile)
        os.unlink(rdatafile.name)
        return return_code

    def _prepare_data(self, queue, tmpfile):
        '''Prepare the queue data for sending'''
        for item in ['memory', 'messages', 'messages_unacknowledged',
                     'consumers']:
            key = '"rabbitmq.queues[{0},queue_{1},{2}]"'
            key = key.format(queue['vhost'], item, queue['name'])
            value = queue.get(item, 0)
            logging.debug("SENDER_DATA: - %s %s" % (key,value))
            tmpfile.write("- %s %s\n" % (key, value))
        ##  This is a non standard bit of information added after the standard items
        for item in ['deliver_get', 'publish']:
            key = '"rabbitmq.queues[{0},queue_message_stats_{1},{2}]"'
            key = key.format(queue['vhost'], item, queue['name'])
            value = queue.get('message_stats', {}).get(item, 0)
            logging.debug("SENDER_DATA: - %s %s" % (key,value))
            tmpfile.write("- %s %s\n" % (key, value))
			

    def _send_data(self, tmpfile):
        '''Send the queue data to Zabbix.'''
        args = 'zabbix_sender -vv -c {0} -i {1}'
        if self.senderhostname:
            args = args + " -s " + self.senderhostname
        return_code = 0
        process = subprocess.Popen(args.format(self.conf, tmpfile.name),
                                           shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        out, err = process.communicate()
        logging.debug("Finished sending data")
        return_code = process.wait()
        logging.info("Found return code of " + str(return_code))
        if return_code == 1:
            logging.error(out)
            logging.error(err)
        else:
            logging.debug(err)
            logging.debug(out)
        return return_code

    def check_aliveness(self):
        '''Check the aliveness status of a given vhost.'''
        return self.call_api('aliveness-test/%2f')['status']

    def check_server(self, item, node_name):
        '''First, check the overview specific items'''
        if item == 'message_stats_deliver_get':
          return self.call_api('overview').get('message_stats', {}).get('deliver_get_details', {}).get('rate',0)
        elif item == 'message_stats_publish':
          return self.call_api('overview').get('message_stats', {}).get('publish_details', {}).get('rate',0)
        elif item == 'rabbitmq_version':
          return self.call_api('overview').get('rabbitmq_version', 'None')
        '''Return the value for a specific item in a node's details.'''
        node_name = node_name.split('.')[0]
        nodeInfo = self.call_api('nodes')
        for nodeData in nodeInfo:
            logging.debug("Checking to see if node name {0} is in {1} for item {2} found {3} nodes".format(node_name, nodeData['name'], item, len(nodeInfo)))
            if node_name in nodeData['name'] or len(nodeInfo) == 1:
                logging.debug("Got data from node {0} of {1} ".format(node_name, nodeData.get(item)))
                return nodeData.get(item)
        return 'Not Found'


def main():
    '''Command-line parameters and decoding for Zabbix use/consumption.'''
    choices = ['list_queues', 'list_shovels', 'list_nodes', 'queues', 'shovels', 'check_aliveness',
               'server']
    parser = optparse.OptionParser()
    parser.add_option('--username', help='RabbitMQ API username', default='guest')
    parser.add_option('--password', help='RabbitMQ API password', default='guest')
    parser.add_option('--hostname', help='RabbitMQ API host', default=socket.gethostname())
    parser.add_option('--protocol', help='Use http or https', default='http')
    parser.add_option('--port', help='RabbitMQ API port', type='int', default=15672)
    parser.add_option('--check', type='choice', choices=choices, help='Type of check')
    parser.add_option('--metric', help='Which metric to evaluate', default='')
    parser.add_option('--filters', help='Filter used queues (see README)')
    parser.add_option('--node', help='Which node to check (valid for --check=server)')
    parser.add_option('--conf', default='/etc/zabbix/zabbix_agentd.conf')
    parser.add_option('--senderhostname', default='', help='Allows including a sender parameter on calls to zabbix_sender')
    parser.add_option('--logfile', help='File to log errors (defaults to /var/log/zabbix/rabbitmq_zabbix.log)', default='/var/log/zabbix/rabbitmq_zabbix.log')
    parser.add_option('--loglevel', help='Defaults to INFO', default='INFO')
    (options, args) = parser.parse_args()
    if not options.check:
        parser.error('At least one check should be specified')
    logging.basicConfig(filename=options.logfile or "/var/log/zabbix/rabbitmq_zabbix.log", level=logging.getLevelName(options.loglevel or "INFO"), format='%(asctime)s %(levelname)s: %(message)s')

    logging.debug("Started trying to process data")
    api = RabbitMQAPI(user_name=options.username, password=options.password,
                      host_name=options.hostname, port=options.port,
                      conf=options.conf, senderhostname=options.senderhostname)
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
    elif options.check == 'list_nodes':
        print json.dumps({'data': api.list_nodes()})
    elif options.check == 'list_shovels':
        print json.dumps({'data': api.list_shovels()})
    elif options.check == 'queues':
        print api.check_queue(filters)
    elif options.check == 'shovels':
        print api.check_shovel(filters)
    elif options.check == 'check_aliveness':
        print api.check_aliveness()
    elif options.check == 'server':
        if not options.metric:
            parser.error('Missing required parameter: "metric"')
        else:
            if options.node:
                print api.check_server(options.metric, options.node)
            else:
                print api.check_server(options.metric, api.host_name)

if __name__ == '__main__':
    main()
