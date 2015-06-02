import socket
import os
import json
import cPickle as pickle
import sys
import argparse
import sqlite3 as lite
import time



def store_file(file_path, size, connection):
    with open(file_path, 'wb') as f:
        print('Filename: ' + os.path.basename(file_path))

        while True:
            # size = int(connection.recv(16))
            print('Total size: ' + str(size))
            recvd = ''
            while size > len(recvd):
                data = connection.recv(1024)
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