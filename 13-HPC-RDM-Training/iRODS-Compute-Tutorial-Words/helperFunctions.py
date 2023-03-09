"""
@licence: Apache 2.0
@Copyright (c) 2017, Christine Staiger (SURFsara)
@author: Christine Staiger
"""
import os
from pathlib import Path

# irods
import irods.keywords as kw


# create directory if it does not exist already
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        

# read all data from folder and concatenate into one string
def files_to_text(dir):
    text = ""
    for child in Path(dir).iterdir():
        if child.is_file():
            with open(child, 'r') as f:
                text = text + f.read()
    return text


# irods helper functions
def parse_query(query_results):
    """
    Parse a query that fetched Collection.name and DataObject.name;
    the function creates the full iRODS path of all yielded files.

    Usage example:
    iParseQuery(sess.query(Collection.name, DataObject.name))
    iParseQuery(sess.query(Collection.name, DataObject.name).filter(
                DataObjectMeta.name == 'author' and DataObjectMeta.value == 'Lewis Carroll'))
    """
    irods_paths = []
    results = query_results.get_results()

    for item in results:
        for k in item.keys():
            if k.icat_key == 'DATA_NAME':
                name = item[k]
            elif k.icat_key == 'COLL_NAME':
                coll = item[k]
            else:
                continue
        irods_paths.append(coll+'/'+name)
    return irods_paths


def get_data(sess, irods_paths, dest_folder):
    """
    Downloads a list of data objects from iRODS and saves them in the destination folder.
    Watch out: Data will be overwritten!
    Example usage:
    iGetList(sess, ['/aliceZone/home/irods-user1/myiPyFun.py'], '/home/user1/dataFilesToCompute')

    Parameters:
    sess    - iRODS session
    iPaths  - List of full iRODS paths to data objects
    destFolder - Location, unix filesystem
    """
    ensure_dir(dest_folder)
    print("Write to: ", dest_folder)
    for path in irods_paths:
        buff = sess.data_objects.open(path, 'r').read()
        with open(dest_folder+'/'+os.path.basename(path), 'wb') as f:
            f.write(buff)


def put_file(sess, filename, irods_dest):
    """
    Uploads a file to iRODS and returns the iRODS data object.
    Watch out: Returns an error if data object already exists.
    Example usage:
    myObj = iPutFile(sess, "/home/user1/pythonscripts/helperFunctions.py", "/aliceZone/home/irods-user1/myiPyFun.py")

    Parameters:
    sess    - iRODS session
    iPath   - Full iRODS paths to destination data object
    fileName - Full path to file, unix filesystem
    """

    options = {kw.REG_CHKSUM_KW: ''}

    sess.data_objects.put(filename, irods_dest, **options)
    obj = sess.data_objects.get(irods_dest)

    return obj


def ils_coll(sess, irods_path):
    """
    Lists the whole iRODS collection recursively.
    Exanple usage:
    iLsColl(sess, '/aliceZone/home/irods-user1')

    Parameters:
    sess    - iRODS session
    iPath   - Full iRODS paths to the iRODS collection
    """

    coll = sess.collections.get(irods_path)
    for src_coll, _, objs in coll.walk():
        print("-C "+src_coll.path)
        print("\n".join(["    "+obj.path for obj in objs]))
