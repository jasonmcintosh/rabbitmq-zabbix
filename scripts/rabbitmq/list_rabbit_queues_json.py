#!/usr/bin/env /usr/bin/python
import list_rabbit_queues_json
from base_rabbit_check import BaseRabbitCheck, make_option
import json

class RabbitQueueList(BaseRabbitCheck):
	"""
	performs a nagios compliant check on a single queue and
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""

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
		queues = []
		for queueData in data:
			elementData = {'{#VHOSTNAME}':queueData['vhost'], '{#QUEUENAME}':queueData['name']}
			queues.append(elementData)
		return json.dumps(queues)
if __name__ == "__main__":
	obj = RabbitQueueList()
	obj.check().exit()
