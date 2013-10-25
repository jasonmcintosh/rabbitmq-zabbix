#!/usr/bin/env /usr/bin/python
import check_rabbit_server
import sys
from base_rabbit_check import BaseRabbitCheck, make_option
import string

class RabbitCheckServer(BaseRabbitCheck):
	"""
	performs a nagios compliant check on a single queue and
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""
	serverOptions=["mem_used","mem_limit","disk_free_limit","disk_free","fd_used","fd_total","proc_used","proc_total","sockets_used","sockets_total"]
	type = make_option("--type", dest="type", help="Type of check - "+str(serverOptions), type="string", default='%2F')
	def makeUrl(self):
		"""
		forms self.url, a correct url to polling a rabbit queue
		"""
		self.url = "http://%s:%s/api/nodes" % (self.options.hostname, self.options.port)

	def testOptions(self):
		if not self.options.type:
			raise Exception("Missing type")
		if not (self.options.type in self.serverOptions):
			raise Exception("Type of " + self.options.type + " is incorrect")
	def parseResult(self, data):
		for result in data:
			if string.split(result['name'], '@')[1] in self.options.hostname:
				nodeData = result
		if nodeData:
			return nodeData[self.options.type]
		return ''


if __name__ == "__main__":
	obj = RabbitCheckServer().check().exit()
