#!/usr/bin/env /usr/bin/python
import check_rabbit_queue
import urllib2
import json
from urllib2 import Request, urlopen, URLError, HTTPError
import time,datetime
import urllib
from base_rabbit_check import BaseRabbitCheck, make_option
from subprocess import call


class RabbitQueueCheck(BaseRabbitCheck):
	"""
	performs a nagios compliant check on a single queue and
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""
	queueOptions=["memory","messages","messages_unacknowledged","consumers"]
	item = make_option("--item", dest="item", help="Queue option to check "+str(queueOptions), type="string", default="messages")


	def makeUrl(self):
		"""
		forms self.url, a correct url to polling a rabbit queue
		"""
		self.url = "http://%s:%s/api/queues" % (self.options.hostname, self.options.port)

	def testOptions(self):
		"""
		returns false if necessary options aren't present
		"""

        def parseResult(self, data):
		for queueData in data:
			#print json.dumps(queueData)
			for itemData in self.queueOptions:
				zabbixKey="\"rabbitmq["+queueData['vhost']+",queue_"+itemData+","+queueData['name']+"]\""
				if queueData.get(itemData):
					zabbixValue=queueData[itemData]
				else:
					zabbixValue=0
				returnCode=call('zabbix_sender -c /etc/zabbix/zabbix_agentd.conf -k '+zabbixKey + ' -o ' + str(zabbixValue))
				print 'Response of ' + returnCode + ' zabbix_sender -c /etc/zabbix/zabbix_agentd.conf -k '+zabbixKey + ' -o ' + str(zabbixValue)
				#print "Looking at item",itemData
		return '0'

if __name__ == "__main__":
	obj = RabbitQueueCheck()
	obj.check().exit()
