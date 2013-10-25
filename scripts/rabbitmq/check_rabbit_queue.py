#!/usr/bin/env /usr/bin/python
import check_rabbit_queue
import urllib2
import json
from urllib2 import Request, urlopen, URLError, HTTPError
import time,datetime
import urllib
from base_rabbit_check import BaseRabbitCheck, make_option


class RabbitQueueCheck(BaseRabbitCheck):
	"""
	performs a nagios compliant check on a single queue and
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""
	queueOptions=["memory","messages","messages_unacknowledged","consumers", "idle_since"]
	vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')
	queue = make_option("--queue", dest="queue", help="Name of the queue in inspect", type="string")
	item = make_option("--item", dest="item", help="Queue option to check "+str(queueOptions), type="string", default="messages")


	def makeUrl(self):
		"""
		forms self.url, a correct url to polling a rabbit queue
		"""
		self.url = "http://%s:%s/api/queues/%s/%s" % (self.options.hostname, self.options.port, urllib.quote(self.options.vhost,''), urllib.quote(self.options.queue))

	def testOptions(self):
		"""
		returns false if necessary options aren't present
		"""
		if not self.options.vhost or not self.options.queue or not (self.options.item in self.queueOptions):
			raise Exception("Missing option... " + str(self.options.item) + " was not in " + str(self.queueOptions) + " or vhost/queue missing:" + str(self.options.vhost) + "," + str(self.options.queue))

        def parseResult(self, data):
                self.queue = self.options.queue
                if data.get(self.options.item):
			if self.options.item == "idle_since":
				return int(time.mktime(datetime.datetime.strptime(data[self.options.item], "%Y-%m-%d %H:%M:%S").timetuple()))
                        return data[self.options.item]
		return '0'

if __name__ == "__main__":
	obj = RabbitQueueCheck()
	obj.check().exit()
