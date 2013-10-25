#!/usr/bin/env /usr/bin/python
import check_rabbit_aliveness
from base_rabbit_check import BaseRabbitCheck, make_option


class RabbitAlivenessCheck(BaseRabbitCheck):
	"""
	performs a nagios compliant check on a single queue and
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""

	vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')


	def makeUrl(self):
		"""
		forms self.url, a correct url to polling a rabbit queue
		"""
		try:
			self.url = "http://%s:%s/api/aliveness-test/%s" % (self.options.hostname, self.options.port, self.options.vhost)
			return True
		except Exception, e:
			self.rabbit_error = 3
			self.rabbit_note = "problem forming api url:", e
		return False

	def testOptions(self):
		"""
		returns false if necessary options aren't present
		"""
		if not self.options.vhost:
			raise Exception("Missing vhost")

	def parseResult(self, data):
		return data['status']

if __name__ == "__main__":
	obj = RabbitAlivenessCheck()
	obj.check().exit()
