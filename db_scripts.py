import sqlite3 as lite

import os

def get_db_path():
    return os.path.join(\
        os.path.dirname(__file__), *['apps.db'])
    
def get_file_by_id( ID, table='Storage'):
    """
    Check if filename with id in db
    return path or None
    
    """
    with lite.connect(get_db_path()) as con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute('SELECT Name, Filepath FROM {0} WHERE ID=:ID'.format(table),\
            {'ID':int(ID)})
        con.commit()
        row = cur.fetchone()
        if row == None: return None
        return (row["Name"], row['Filepath'])

def is_stored( filename, ID):
    """
    Check filename == f_name retrieved by ID, return True
    Otherwise: return False
    """
    result = get_file_by_id(ID)
    if result == None: # ID is empty
        return False
    f_name, f_path = result
    return filename == f_name # True file stored | False - not stored

def db_add_entry( ID, filename, target_path):
    entry = {
        'ID': ID,
        'Filename':filename, 
        'Filepath':target_path
    }
    with lite.connect(get_db_path()) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Storage VALUES({ID}, '{Filename}', '{Filepath}')".format(**entry))

def delete_entry( ID):
    with lite.connect(get_db_path()) as con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("DELETE FROM Storage WHERE ID = {0}".format(ID))

def select_range( _range):
    sql_req, result = None, []
    if not _range:
        sql_req = 'SELECT ID,Filepath FROM Storage'
    else:
        _min, _max = _range
        sql_req = 'SELECT ID,Filepath FROM Storage WHERE ID BETWEEN {0} AND {1}'.format(_min, _max)
    with lite.connect(get_db_path()) as con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(sql_req)
        rows = cur.fetchall()
        for row in rows:
            result.append([row['ID'], row['Filepath']])
    return result # list of rows