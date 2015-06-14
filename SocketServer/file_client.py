import socket
import sys
import os
import json
import time
import cPickle as pickle
from contextlib import contextmanager
import common as lib
import argparse


class Client(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port

	@contextmanager
	def connect_to_server(self):
		print 'Trying to connect...'
		s = socket.socket()
		try:
			s.connect((self.host, self.port))
			yield s
		except Exception, e:
			print e
		finally:
			s.close()
	

	def backup_file(self, file_path, ID):
		"""
		Send file if not exist on server
		"""
		assert os.path.exists(file_path), 'Path does not exist!'
		request,payload = {'action':'backup'}, None
		request['filename'] = os.path.basename(file_path)
		request['ID'] = ID
		request['size'] = size = os.path.getsize(file_path)
		
		with self.connect_to_server() as connection:
			print 'sending info', request
			connection.sendall(json.dumps(request)) # request
			response = connection.recv(1024)
			if response != 'EXISTS':
				print 'sending file'
				lib.send_file(connection, file_path)
				# connection.sendall(payload)
			else:
				print 'File : {0} with ID: {1} already stored!'.format(file_path, ID)
			
		
	def restore_file(self, directory, ID, rewrite=False):
	    """
	    Get file by ID from server,
	    Store to local folder,
	    if rewrite is False - resolve name conflict
	    otherwise rewrite file
	    """
	    request,response = {},None
	    request['action'] ='restore'
	    request['ID'] = ID
	    request['rewrite'] = rewrite

	    with self.connect_to_server() as connection:
			connection.sendall(json.dumps(request)) # request
			try:
				response = json.loads(connection.recv(1024))
			except Exception:
				print 'No entries found with ID: ', ID
				return 
			if response != 'FILE_NOT_FOUND':
				# should be filename
				f_name,size = map(response.get, ('filename', 'size'))
				file_path = lib.get_target_path(f_name, dirname=directory, rewrite=rewrite)
				lib.store_file(file_path, size, connection)
			else:
				print 'File not found'


	def list_entries(self, _range=[]):
	    """
	    print out entries of specified range
	    if no range, print all
	    """
	    request = {}
	    request['action'] ='list'
	    request['range'] = _range

	    with self.connect_to_server() as connection:
			connection.sendall(json.dumps(request)) # request
			response = json.loads(connection.recv(1024))
			if len(response)>0:
				for _id, path in response:
					print _id, '  :  ', path
			else:
				print 'No entries found!'


	def remove_files(self, ID):
	    """
	    Remove specified files by ID
	    from storage 
	    """
	    print 'Got ID: ', ID
	    request = {}
	    request['action'] ='delete'
	    request['ID'] = ID
	    with self.connect_to_server() as connection:
			connection.sendall(json.dumps(request))
			resp = json.loads(connection.recv(1024))
			print resp

	


def parse_arguments():

	argparser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description="server for backup and restore files",
		epilog=	"""
				Correct combination of arguments:
				--backup FILE ID;
				--restore DIRECTORY ID [-R];
				--list [ID_RANGE];
				--del ID;
				"""
	)
	argparser.add_argument("--list", help="list entries by range ", type=int, nargs='*')
	argparser.add_argument("--backup", help="backs up file with unique ID ", nargs=2)
	argparser.add_argument("--restore", help="brings file from server to client ", nargs=2)
	argparser.add_argument("--delete", help="delete file on server by ID ",type=int, nargs=1)
	argparser.add_argument("-R", "--rewrite", action='store_true', help="Rewrite file if True")
	argparser.add_argument("--host", type=str, help="host to connect to", default='localhost')
	argparser.add_argument("--port", type=int, help="port to connect to", default=1234)
	
	# args = argparser.parse_args()
	return argparser
	
def main():
	argparser = parse_arguments()
	args = argparser.parse_args()
	client = Client(args.host, args.port)

	if args.backup:
		path, ID = args.backup
		assert os.path.isfile(path), \
			'Path should be a valid file path'
		client.backup_file(path, int(ID))

	elif args.restore:
		path, ID = args.restore
		client.restore_file(path, int(ID), args.rewrite)

	elif isinstance(args.list, list):
		if len(args.list) == 2:
			client.list_entries(_range=args.list)
		else:
			client.list_entries()

	elif args.delete:
		ID = int(args.delete.pop())
		client.remove_files(ID)

	else:
		argparser.print_help()
		

if __name__ == '__main__':
	main()


