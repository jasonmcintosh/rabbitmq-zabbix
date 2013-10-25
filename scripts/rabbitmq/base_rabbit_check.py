#!/usr/bin/env /usr/bin/python

import abc
import urllib2
import json
import sys
from optparse import Option, make_option, OptionParser
from urllib2 import Request, urlopen, URLError, HTTPError
import base_rabbit_check
class PluginMeta(type):
    """
    We use a metaclass to create the plugins in order to gather and
    set up things such as command line arguments.
    """

    def __new__(cls, name, bases, attrs):
        attrs = attrs if attrs else {}

        # Set the options on the plugin by finding all the Options and
        # setting them. This also removes the original Option attributes.
        options = []

        for key,val in attrs.items():
            if isinstance(val, Option):
                # We set the destination of the Option to always be the
                # attribute key...
                val.dest = key

                # Append it to the list of options and delete it from
                # the original attributes list
                options.append(val)
                del attrs[key]

        # Need to iterate through the bases in order to extract the
        # list of parent options, so we can inherit those.
        for base in bases:
            if hasattr(base, "_options"):
                options.extend(getattr(base, "_options"))

        # Store the option list and create the option parser
        attrs["_options"] = options
        attrs["_option_parser"] = OptionParser(option_list=options)

        # Create the class
        return super(PluginMeta, cls).__new__(cls, name, bases, attrs)

class BaseRabbitCheck(object):
	__metaclass__ = PluginMeta
	hostname = make_option("-H", "--hostname")
	timeout = make_option("-t", "--timeout", type="int")
	verbosity = make_option("-v", "--verbose", action="count")
	def __init__(self, args=sys.argv):
		(self.options, self.args) = self._option_parser.parse_args(args)

	"""
	performs a nagios compliant check
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""

	username = make_option("--username", dest="username", help="RabbitMQ API username", type="string", default="guest")
	password = make_option("--password", dest="password", help="RabbitMQ API password", type="string", default="guest")
	port = make_option("--port", dest="port", help="RabbitMQ API port", type="string", default="15672")
	result=""
	exit_code=0
	def doApiGet(self):
		"""
		performs and returns content from an api get
		"""
		password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password(None, self.url, self.options.username, self.options.password)
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)

		response = None
		request = opener.open(self.url)
		response = request.read()
		request.close()

		return response

	def parseJson(self, response):
		"""
		parse test and return api json
		"""
		data = json.loads(response)
		return data

	@abc.abstractmethod
	def makeUrl(self):
		raise Exception("Undefined!")

	@abc.abstractmethod
	def testOptions(self):
		raise Exception("Undefined!")

	@abc.abstractmethod
	def parseResult(self, data):
		raise Exception("Undefined!")


	def check(self):
		"""
		returns a response and perf data for this check
		"""

		if not self.options.hostname or not self.options.port or not self.options.username or not self.options.password:
			raise Exception("Missing several default required parameters!")
		self.makeUrl()
		response = self.doApiGet()

		data = self.parseJson(response)

		self.result = self.parseResult(data)
		return self 

	def exit(self):
		"""
		This prints out the response to ``stdout`` and exits with the
		proper exit code.
		"""
		print(str(self.result))
		sys.exit(self.exit_code)
