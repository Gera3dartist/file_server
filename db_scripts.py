import sqlite3 as lite

import os

class DBHandler(object):

    def __init__(self, db_path=None, table='Storage'):
        self.table = table
        if db_path and 'test' in db_path:
            self.db_path = db_path
            self.initialize_db(db_path)
        elif not db_path:
            self.db_path = self.get_default_db_path()
        else:
            self.db_path = db_path

    def initialize_db(self, db_path):
        '''db initializer'''
        with lite.connect(self.get_db_path()) as con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS {0} (ID INT, Name TEXT, Filepath TEXT)'\
                .format(self.table))

    def get_default_db_path(self):
        return os.path.join(\
            os.path.dirname(__file__), *['apps.db'])

    def get_db_path(self):
        return self.db_path

    def get_file_by_id(self, ID):
        """
        Check if filename with id in db
        return path or None
        
        """
        with lite.connect(self.get_db_path()) as con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute('SELECT Name, Filepath FROM {0} WHERE ID=:ID'.format(self.table),\
                {'ID':int(ID)})
            con.commit()
            row = cur.fetchone()
            if row == None: return None
            return (row["Name"], row['Filepath'])

    def is_stored(self, filename, ID):
        """
        Check filename == f_name retrieved by ID, return True
        Otherwise: return False
        """
        result = self.get_file_by_id(ID)
        if result == None: # ID is empty
            return False
        f_name, f_path = result
        return filename == f_name # True file stored | False - not stored

    def db_add_entry(self, ID, filename, target_path):
        entry = {
            'Table': self.table,
            'ID': ID,
            'Filename':filename, 
            'Filepath':target_path
        }
        with lite.connect(self.get_db_path()) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO {Table} VALUES({ID}, '{Filename}', '{Filepath}')".format(**entry))

    def delete_entry(self, ID):
        with lite.connect(self.get_db_path()) as con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("DELETE FROM {0} WHERE ID = {1}".format(self.table, ID))



    def select_range(self, _range=None):
        sql_req, result = None, []
        if not _range:
            sql_req = 'SELECT ID,Filepath FROM {0}'.format(self.table)
        else:
            _min, _max = _range
            sql_req = 'SELECT ID,Filepath FROM {2} WHERE ID BETWEEN {0} AND {1}'.format(_min, _max, self.table)
        with lite.connect(self.get_db_path()) as con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute(sql_req)
            rows = cur.fetchall()
            for row in rows:
                result.append([row['ID'], row['Filepath']])
        return result # list of rows

    def drop_table(self):
        with lite.connect(self.get_db_path()) as con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS {0}".format(self.table))

