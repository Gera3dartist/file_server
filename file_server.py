import socket
import os
import json
import cPickle as pickle
import sys
import argparse
import sqlite3 as lite
import time
import common as lib
import db_scripts as db

class Server(object):

    def __init__(self,port=1234, directory=None, db=None):
        self.port = port
        self.dirname = directory
        self.db = db


    def backup_file(self,request, connection):
        """
        store file, if file with ID not in db
        otherwise
        do nothing send message to client
        """
        filename, ID, size = request.get('filename'), request.get('ID'), request.get('size')
        file_path = lib.get_target_path(filename, dirname=self.dirname)
        if not db.is_stored(filename, ID):
            print 'Storing file: {0}, ID: {1}'.format(filename, ID)
            # add entry to db
            db.db_add_entry(ID, filename, file_path)
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
        result = db.get_file_by_id(ID)
        if result == None:
            connection.sendall('FILE_NOT_FOUND')
            return 
        else:
            f_name, f_path = result
            with open(f_path, 'rb') as f: 
                payload = f.read()
            response['size'] = size = str('%16d' % len(payload)).strip()
            response['filename'] = f_name
            connection.sendall(json.dumps(response))
            connection.sendall(payload)
            print "File sent"
            

    def list_entries(self, request, connection):
        """
        List entries within specified range,
        If no range specified, list ALL entries
        """
        resp = None
        _range = request.get('range')
        try:
            resp = db.select_range(_range)
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

        result = db.get_file_by_id(ID)
        if not result:
            print 'Entry with ID: {0} not found!'.format(ID)
            connection.sendall(json.dumps(['FILE_NOT_FOUND']))
            return
        _, f_path = result
        db.delete_entry(ID)
        if os.path.exists(f_path):
            os.remove(f_path)
        connection.sendall(json.dumps(['OK']))


    def request_handler(self, connection):
        actions = {
            'backup'  : self.backup_file,
            'restore' : self.restore_file,
            'list'    : self.list_entries,
            'delete'  : self.remove_files
        }
        request = json.loads(connection.recv(1024))
        print 'Got request: {0}'.format(request)
        handler = actions.get(request.get('action'))
        if handler == None:
            connection.sendall('Requested action not found: {0}'.format(action))
            # implement error handling here
            return
        return handler(request, connection)

    def run_server(self, host='', port=1234):
        print('Waiting for clinet to connect...')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        try:
            while True:
                connection, client_address = sock.accept()
                print >> sys.stderr, 'Connection from', client_address
                try:
                    self.request_handler(connection)
                    print 'request done!'
                finally:
                    if connection:
                        time.sleep(2.0)
                        connection.close()
                        print "connection killed: ", client_address
        except Exception, e:
            print e
        finally:
            sock.close()

def parse_arguments():
    argparser = argparse.ArgumentParser(
        description="server for backup and restore files")
    argparser.add_argument("-d", "--directory", help="File id", default="")
    argparser.add_argument("-p","--port", help="File path ", type=int, default=1234)
    args = argparser.parse_args()
    return args


def main():
    args = parse_arguments()
    serv = Server()
    serv.run_server()


if __name__ == '__main__':
    main()      
    