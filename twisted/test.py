from twisted_file_server import FileBackupFactory
from twisted.trial import unittest as ut
from twisted.test import proto_helpers
from db_scripts import DBHandler
from os.path import *
import json


class FileBackupBackEndTestCase(ut.TestCase):
	def setUp(self):
		"""
		Setup phazes:

		- Initialize test_db with test data
		- Initialize Protocol's factory
		- fake transport layer with proto_helpers.StringTransport()
		- simulate connection
		"""
		self.test_db = join(dirname(abspath(__file__)), *['tests','test.db'])
		self.test_db_handler = DBHandler(db_path=self.test_db)
		db_entries = [
			(1, 'file1','/path/to/file1'),
			(2, 'file2','/path/to/file2')
		]
		for _id, name, path in db_entries:
			self.test_db_handler.db_add_entry(_id, name, path)
		factory = FileBackupFactory(db_handler=self.test_db_handler)
		self.proto = factory.buildProtocol(('127.0.0.1', 0))
		self.tr = proto_helpers.StringTransport()
		self.proto.makeConnection(self.tr)

	def tearDown(self):
		"""
		Remove test db afte test has finished
		"""
		self.test_db_handler.drop_table()
		
	def get_request(self, key):
		"""
		Simulates client's requests.
		Returns dumped dictionary
		"""
		req = {
			'b_exists':{'action': 'backup', 'size': 0, 'ID': 1, 'name': 'file1'},
			'b_new':{'action': 'backup', 'size': 0, 'ID': 3, 'name': 'file3'}
		}
		return json.dumps(req.get(key))

	def _test(self, request, expected):
		"""
		Performs testing, by 'sending' requests to server
		and comparing response with expected result
		"""
		self.proto.dataReceived('{0}\r\n'.format(request))
		self.assertEqual(str(self.tr.value()).strip(), expected)

	def test_backup_stored_file(self):
		"""
		test server behavior if file is already stored 
		"""
		self._test(self.get_request('b_exists'), 'EXISTS')

	def test_backup_new_file(self):
		"""
		test server behavior if file is new
		"""
		self._test(self.get_request('b_new'), 'READY')





