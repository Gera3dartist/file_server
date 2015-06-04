import SocketServer, unittest, threading
import os
import sys
sys.path.append(r"C:\Users\Gera\Dropbox\Python\file_server")
from file_client import Client
from file_server import Server
from common import store_file

class TestServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

class RequestHandler(SocketServer.BaseRequestHandler):
	serv_storage = r"C:\Users\Gera\Dropbox\Python\file_server\Tests\test_server_storage"

	def handle(self):
	    # Echo the back to the client
	    data = self.request.recv(1024)
	    _request = json.loads(data)
	    backup(_request)
	    return

	def backup(self,_request):
	    filename, ID, size = _request.get('filename'), _request.get('ID'), _request.get('size')
	    file_path = lib.get_target_path(filename, dirname=serv_storage)
	    store_file(file_path, size, self.request)
 

class ClientBackUpTest(unittest.TestCase):
	def setUp(self):
		self.backup_file = r"C:\Users\Gera\Dropbox\Python\file_server\Tests\test_client_storage\test_backup_data"
		self.restore_file = r"C:\Users\Gera\Dropbox\Python\file_server\Tests\test_server_storage\test_restore_data"
		host_port = ('', 50001)
		self.server = TestServer(('', 50001), RequestHandler)
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		# self.server = Server(*host_port)
		self.client = Client(*host_port)
		# self.server.run_server()
		self.server_thread.start()


	def tearDown(self):
		self.client = None
		self.server = None
		# self.server.server_close()
		os.remove(self.backup_file)


	def test_backup(self):
		"""testing backup"""
		self.client.backup_file(self.backup_file, 1)
		pass
	
	

if __name__ == '__main__':
	unittest.main()

