import socket
import os
import json
import cPickle as pickle
import sys
import argparse
import sqlite3 as lite
import time


def measure_time(f):
    def wrap(*args, **kwargs):
        start = time.time()
        f(*args, **kwargs)
        end = time.time()
        took = end - start
        print 'Time elapsed: ', took
    return wrap

@measure_time
def send_file(sock, file_path):
    with open(file_path, 'rb') as f:

        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            sock.sendall(chunk)
        print('File sent.')


def send_file_in_chunks(file_path, chunk_size=4096):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break

def store_file(file_path, size, sock):
    with open(file_path, 'wb') as f:
        print('Filename: ' + os.path.basename(file_path))

        while True:
            # size = int(sock.recv(16))
            print('Total size: ' + str(size))
            recvd = ''
            while size > len(recvd):
                data = sock.recv(1024)
                if not data: 
                    break
                recvd += data
                f.write(data)
            break
        print('File received.')

def handle_duplicate(file_path):
    import time
    t_stamp = time.strftime("%Y%m%d-%H%M%S")
    path, ext = os.path.splitext(file_path)

    new_path = path + t_stamp + ext
    return new_path

def get_target_path(filename, dirname=None, rewrite=False):
    file_path = None
    if not dirname:
        dirname = os.path.join(os.path.dirname(__file__),'Storage') # getcwd() is wrong here
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    file_path = os.path.join(dirname, filename)
    if os.path.exists(file_path):
        if rewrite:
            os.remove(file_path)
        else:
            file_path = handle_duplicate(file_path)
    return file_path

def server_CLI():
    argparser = argparse.ArgumentParser(
        description="server for backup and restore files")
    argparser.add_argument("-d", "--directory", help="File id", default="")
    argparser.add_argument("--port", help="application port", type=int, default=1234)
    argparser.add_argument("--host", help="application host", default='')
    return argparser

def client_CLI():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="server for backup and restore files",
        epilog= """
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

if __name__ == '__main__':
    path = r"X:\IT_stuff\Games\!!!___FIRST_SEND_.rar"
    for el in send_file_in_chunks(path):
        print el
        print '\n\n len: ', len(el)
        break