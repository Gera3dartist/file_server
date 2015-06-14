import socket
import os
import json
import SocketServer
import traceback
import sys
import argparse
import sqlite3 as lite
import time
import common as lib
from db_scripts import DBHandler


class Requests(object):
    def __init__(self, db_handler=None, dirname=None):
        self.dirname = dirname
        if not db_handler:
            self.db_handler = DBHandler()
        else:
            self.db_handler = db_handler


    def backup_file(self,request, connection):
        """
        store file, if file with ID not in db
        otherwise
        do nothing send message to client
        """
        filename, ID, size = request.get('filename'), request.get('ID'), request.get('size')
        file_path = lib.get_target_path(filename, dirname=self.dirname)
        if not self.db_handler.is_stored(filename, ID):
            print 'Storing file: {0}, ID: {1}'.format(filename, ID)
            # add entry to db
            self.db_handler.db_add_entry(ID, filename, file_path)
            # store entry
            connection.sendall('WRITING')
            lib.store_file(file_path, size, connection)
            connection.sendall('STORED!')

        else:
            print 'File: {0} ID: {1} already stored!'.format(filename, ID)
            connection.sendall('EXISTS')

    def restore_file(self, request, connection):
        """
        Select file by ID, send to client
        """
        ID, payload, response = str(request.get('ID')),None,{}
        result = self.db_handler.get_file_by_id(ID)
        if result == None:
            connection.sendall('FILE_NOT_FOUND')
            return 
        else:
            f_name, f_path = result
            response['size'] = size = os.path.getsize(f_path)
            response['filename'] = f_name
            connection.sendall(json.dumps(response))
            lib.send_file(connection, f_path)
            print "File sent"
            
    def list_entries(self, request, connection):
        """
        List entries within specified range,
        If no range specified, list ALL entries
        """
        resp = None
        _range = request.get('range')
        try:
            resp = self.db_handler.select_range(_range)
            print 'listing items...'
            print resp
            connection.sendall(json.dumps(resp))
        except Exception, e:
            connection.sendall(json.dumps([e]))

    def remove_files(self, request, connection):
        """
        Remove specified files 
        from file system and db
        """
        ID = int(request.get('ID'))

        result = self.db_handler.get_file_by_id(ID)
        if not result:
            print 'Entry with ID: {0} not found!'.format(ID)
            connection.sendall(json.dumps(['FILE_NOT_FOUND']))
            return
        _, f_path = result
        self.db_handler.delete_entry(ID)
        if os.path.exists(f_path):
            os.remove(f_path)
        connection.sendall(json.dumps(['OK']))

class TCPRequestHandler(SocketServer.BaseRequestHandler):
    """
    
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    """

    @classmethod
    def initialize_requests(cls, requests):
        cls.custom_requests = requests

    def get_actions(self):
        return {
            'backup'  : self.custom_requests.backup_file,
            'restore' : self.custom_requests.restore_file,
            'list'    : self.custom_requests.list_entries,
            'delete'  : self.custom_requests.remove_files
        }

    def handle(self):
        connection = self.request
        actions = self.get_actions()
        request = json.loads(connection.recv(1024))
        print 'Got request: {0}'.format(request)
        handler = actions.get(request.get('action'))
        if handler == None:
            connection.sendall('Requested action not found: {0}'.format(action))
            # implement error handling here
            return
        try:
            handler(request, connection)
        except:
            traceback.print_exc(file=sys.stdout)
   
        finally:
            connection.close()
            print 'awiting connection...'

    

# http://stackoverflow.com/questions/20745352/creating-a-multithreaded-server-using-socketserver-framework-in-python
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    pass

#################################
# CLI
#################################





def main():
    argparser = lib.server_CLI()
    args = argparser.parse_args()
    _requests = Requests(dirname=args.directory)
    TCPRequestHandler.initialize_requests(_requests)
    ThreadedTCPServer((args.host,args.port), TCPRequestHandler).serve_forever()


if __name__ == '__main__':
    main()      
    