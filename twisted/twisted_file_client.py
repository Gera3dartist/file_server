from __future__ import print_function
import sys
import os
import json
from os.path import *
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

sys.path.append(dirname(dirname(abspath(__file__))))
import common as lib

class EchoClient(LineReceiver):
	end = 'END'

	def __init__(self, request):
		self.request = request
		self.remote = self.request.copy()
		self.remote.update({'name':basename(self.remote.get('path'))})
		self.remote.pop('path', None)

	def connectionMade(self):
		"""send request here"""
		print ('connectionMade')
		self.sendLine(json.dumps(self.remote))


	def lineReceived(self, line):
		"""handle server responses in here"""
		print('receive: ', line)
		if line == self.end:
			print('END!')
			self.transport.loseConnection()
		if line ==  'READY':
			self.backup_file()
		elif line == 'EXISTS':
			file_path, ID = map(self.request.get, ('path', 'ID'))
			print('File : {0} with ID: {1} already stored!'.\
				format(file_path, ID))
			self.transport.loseConnection()

	def rawDataReceived(self, data):
		pass


	def backup_file(self):
		"""
		Send file if not exist on server
		"""
		file_path = self.request.get('path')
		print('sending file {0}'.format(file_path))
		for bytes in lib.send_file_in_chunks(file_path):
			self.transport.write(bytes)
		self.transport.write('END\r\n')

			
			

class EchoClientFactory(ClientFactory):
	protocol = EchoClient

	def __init__(self,request):
		self.request = request
		self.done = Deferred()

	def clientConnectionFailed(self, connector, reason):
		print ('connection failed:', reason.getErrorMessage())
		self.done.addErrback(reason)

	def clientConnectionLost(self, connector, reason):
		print ('connection lost: ', reason.getErrorMessage())
		self.done.callback(None)

	def buildProtocol(self, addr):
		p = self.protocol(self.request)
		p.factory = self
		return p



def main(reactor):
	
	request = {}
	argparser = lib.client_CLI()
	args = argparser.parse_args()

	if args.backup:
		path, ID = args.backup
		assert os.path.isfile(path), \
			'Path should be a valid file path'
		# client.backup_file(path, int(ID))
		size = getsize(path)
		request.update({'action':'backup', 'path':path, 'ID':int(ID), 'size':size})

	elif args.restore:
		path, ID = args.restore
		# client.restore_file(path, int(ID), args.rewrite)
		request.update({'action':'restore','path':path, 'ID':int(ID), 'rewrite': args.rewrite})
	elif isinstance(args.list, list):
		if len(args.list) == 2:
			# client.list_entries(_range=args.list)
			request.update({'action':'list', '_range':args.list})
		else:
			# client.list_entries()
			request.update({'action':'list'})
	elif args.delete:
		ID = int(args.delete.pop())
		# client.remove_files(ID)
		request.update({'action':'delete', 'ID':ID})
	else:
		argparser.print_help()
		sys.exit(0)


	factory = EchoClientFactory(request=request)
	reactor.connectTCP('localhost', 1234, factory)
	return factory.done

if __name__ == '__main__':
	task.react(main)


