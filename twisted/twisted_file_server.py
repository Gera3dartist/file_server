from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols import basic
from os.path import *
import sys
import json
sys.path.append(dirname(dirname(abspath(__file__))))
from db_scripts import DBHandler
import common as lib


class FileTransferProtocol(basic.LineReceiver):
	END = 'END\r\n'
	def __init__(self, db_handler=None, _dirname=None):
		self.__directory = _dirname
		if not db_handler:
			self.db_handler = DBHandler()
		else:
			self.db_handler = db_handler

	def connectionMade(self):
		self.file_handler = None
		self.file_path = None
		self.request = None
		self.request_handler = None
		# self.sendLine('Connection established')

	
	def lineReceived(self, line):
		# print ('got request: ',line )		
		if not self.request:
			self.request = json.loads(line)
			print ('got request: ',self.request )		
		if not self.request_handler:
			self.request_handler = self.get_handler(self.request)
			self.request_handler()


	def rawDataReceived(self, data):
		
		if not self.file_path:
			filename = self.request.get('name')
			self.file_path = lib.get_target_path(filename, dirname=self.__directory)
		if not self.file_handler:
			self.file_handler = open(self.file_path, 'wb')
		
		if self.END in data:
			# Last chunk
			data = data[:len(self.END)]
			self.file_handler.write(data)
			self.file_handler.close()
			# add to db
			self.add_entry_to_db()
			print ('file is stored')
			self.setLineMode()
			self.transport.write(self.END)
		else:
			self.file_handler.write(data)
		

	def get_handler(self, request):
		action = request.get('action')
		actions = {
			'backup'  : self.backup_file,
			# 'restore' : self
			# 'list'    : self
			# 'delete'  : self
		}

		return actions.get(action)

	def backup_file(self):
		"""
		store file, if file with ID not in db
		otherwise
		do nothing send message to client
		"""
		filename, ID, size = map(self.request.get,('name', 'ID','size'))
		# file_path = lib.get_target_path(filename)
		if not self.db_handler.is_stored(filename, ID):
			print 'Storing file: {0}, ID: {1}'.format(filename, ID)
			self.sendLine('READY\r\n')
			self.setRawMode()
		else:
			print 'File: {0} ID: {1} already stored!'.format(filename, ID)
			self.sendLine('EXISTS\r\n')

	def add_entry_to_db(self):
		filename, ID = map(self.request.get,('name', 'ID'))
		if not self.db_handler.is_stored(filename, ID):
			self.db_handler.db_add_entry(ID, filename, self.file_path)


class FileBackupFactory(protocol.Factory):
	protocol = FileTransferProtocol

	def __init__(self, _dirname=None, db_handler=None):
		self._dirname = _dirname
		self.db_handler = db_handler

	def buildProtocol(self, addr):
		p = self.protocol(_dirname=self._dirname, db_handler=self.db_handler)
		p.factory = self
		return p
		

def main():
	argparser = lib.server_CLI()
	args = argparser.parse_args()
	endpoint = TCP4ServerEndpoint(reactor, args.port)
	endpoint.listen(FileBackupFactory(args.directory))
	reactor.run()

if __name__ == '__main__':
	main()




