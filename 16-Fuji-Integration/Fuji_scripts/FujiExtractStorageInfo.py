#!/usr/bin/env python3

from irods.session import iRODSSession
import subprocess
import getopt
import os, sys

from irods.exception import CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME, \
                            CAT_NO_ACCESS_PERMISSION, CAT_SUCCESS_BUT_WITH_NO_INFO

def addMetadata(item, key, value, units = None):
    """
    Adds metadata to all items
    items: list of iRODS data objects or iRODS collections
    key: string
    value: string
    units: (optional) string 

    Throws:
        CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME
    """
    try:
        item.metadata.add(key.upper(), value, units)
    except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
        print(RED+"INFO ADD META: Metadata already present"+DEFAULT)
    except CAT_NO_ACCESS_PERMISSION:
        raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions")

        

def updateMetadata(item, key, value, units = None):
    """
    Updates a metadata entry to all items
    items: list of iRODS data objects or iRODS collections
    key: string
    value: string
    units: (optional) string

    Throws: CAT_NO_ACCESS_PERMISSION
    """
    try:
        if key in item.metadata.keys():
            meta = item.metadata.get_all(key)
            valuesUnits = [(m.value, m.units) for m in meta]
            if (value, units) not in valuesUnits:
                #remove all iCAT entries with that key
                for m in meta:
                    item.metadata.remove(m)
                #add key, value, units
                addMetadata(item, key, value, units)

        else:
            addMetadata(item, key, value, units)
    except CAT_NO_ACCESS_PERMISSION:
        raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions "+item.path)



def deleteMetadata(item, key, value, units=""):
    """
    Deletes a metadata entry of all items
    items: list of iRODS data objects or iRODS collections
    key: string
    value: string
    units: (optional) string

    Throws:
        CAT_SUCCESS_BUT_WITH_NO_INFO: metadata did not exist
    """
    try:
        item.metadata.remove(key, value, units)
    except CAT_SUCCESS_BUT_WITH_NO_INFO:
        print(RED+"INFO DELETE META: Metadata never existed"+DEFAULT)
    except CAT_NO_ACCESS_PERMISSION:
        raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions "+item.path)

def stageObj(storagePath):
    cmd_stage = ["s3cmd", "--no-check-certificate", "restore"]
    p = subprocess.Popen(cmd_stage+[storagePath],stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()

    return out, err


def getState(storagePath, irodsObj):
    cmd_status = ["s3cmd", "--no-check-certificate", "info", "-d"]
    p = subprocess.Popen(cmd_status+[storagePath],stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    #result is in err
    info = [line for line in err.decode().split('\n') if not "DEBUG" in line]
    ongoing = [line for line in info if 'x-amz-restore' in line]
    if ongoing == []:
        updateMetadata(irodsObj, "FUJI_STATE", "offline")
        print(irodsObj.path, "FUJI_STATE: offline")
    elif 'ongoing-request="true"' in ongoing[0]:
        updateMetadata(irodsObj, "FUJI_STATE", "staging")
        print(irodsObj.path, "FUJI_STATE: staging")
    elif 'ongoing-request="false"' in ongoing[0]:
        expDateIdxStart = err.decode().index('expiry')
        date = ''.join([d.strip() for d in (err.decode()[expDateIdxStart:].split('\n')[:2])])
        dateFormatted = date.split("=")[1].replace("'", "").replace("\\", "").replace('"', '').strip(',')
        updateMetadata(irodsObj, "FUJI_STATE", "online")
        updateMetadata(irodsObj, "FUJI_ONLINE_EXPIRY_DATE", dateFormatted)
        print(irodsObj.path, "FUJI_STATE: online")
        print(irodsObj.path, "FUJI_ONLINE_EXPIRY_DATE", dateFormatted)
    return out, err


def main(argv):
    #CONFIGS
    envFile = os.environ['HOME']+"/.irods/irods_environment.json"
    tapeRescName = "fuji"
    #Setup
    session = iRODSSession(irods_env_file=envFile)
    fujiResc = session.resources.get(tapeRescName)
    physPath = "s3:/"+fujiResc.vault_path #extend with logical path starting with 'home'

    try:
        opts, args = getopt.getopt(argv,"hisp:",["info=", "stage=", "irodspath="])
    except getopt.GetoptError:         
        print('./FujiExtractStorageInfo.py -h')
        sys.exit(2)
    
    stage = False
    info = False
    irodsObj = None
    for opt, arg in opts:
        if opt == '-h':
            print('Fuji tape library client for staging and retrieving info.')
            print('USAGE:')
            print('Retrieving info from tape:')
            print('\t ./FujiExtractStorageInfo.py -i -p <iRODS Path>')
            print('Staging data when offline:')
            print('\t ./FujiExtractStorageInfo.py -s -p <iRODS Path>')
            sys.exit(0)
        elif opt in ['-i', '--info']:
            print("Retrieving state info and adding to data object in iRODS.")
            info  = True
        elif opt in ['-s', '--stage']:
            print("Staging data object to disk.")
            stage = True
        elif opt in ['-p', '--irodspath']:
            print('\t'+arg)
            irodsObj = session.data_objects.get(arg)
            if irodsObj.resource_name != tapeRescName:
                print("Data not on tape. Resource:", irodsObj.resource_name)
                sys.exit(2)
    if irodsObj == None:
        print('No iRODS path given.')
        sys.exit(2)
    if stage and info:
        print('Choose either staging or info.')
        sys.exit(2)
    if not stage and not info:
        print('No operation chosen.')
        sys.exit(2)

    if irodsObj.resource_name == tapeRescName:
        storagePath = physPath + irodsObj.path.split(session.zone)[1]
        if stage:
            stageObj(storagePath)
        if info:
            getState(storagePath, irodsObj)


if __name__ == "__main__":
   main(sys.argv[1:])

