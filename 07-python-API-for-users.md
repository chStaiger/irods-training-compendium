# Introduction Python API for iRODS

**Authors**
- Arthur Newton (SURFsara)
- Christine Staiger (SURFsara)
- Claudia Behnke (SURFsara)

**License**
Copyright 2018 SURFsara BV

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Goal
You will learn how to interact with iRODS via the python API. In this module we will explore the API in interactive mode. You will:

- Up and download data
- Up and download data collections
- Add and edit metadata
- Set Accession control lists for data objects and collections
- Query for data using user defined metadata

## Exploring the python API to iRODS in ipython

### Material and data for this module

We prepared some data for you. Please clone the repository to  your home folder:

```
git clone https://git.wur.nl/staig001/irodstraining.git
cd ~/irodstraining
```

### Prerequisites
- Credentials and access to an iRODS instance
- [python-irodsclient](https://github.com/irods/python-irodsclient)

Install the *irods-pythonclient* (for python3 use pip3):

```
pip install git+https://github.com/irods/python-irodsclient.git@master --user
```

Start a python session or a session in an interactive python environment e.g. ipython or ipython3:

```sh
ipython
```

## Data objects
### Connect to iRODS
To connect 

The module *getpass* asks for passwords without printing the input on screen. With en encoding function we prevent that the variable contains the plain password when we pass it to the iRODS server.

```py
import getpass
pw = getpass.getpass().encode()
```
Now we can create an iRODS session:
```
from irods.session import iRODSSession
session = iRODSSession(host='sara-alice.grid.surfsara.nl', 
					   port=1247, user='irods-user1', 
					   password=pw.decode(), zone='aliceZone', 
					   **{"irods_default_hash_scheme": "MD5"})
```

Note that you will need to change the username to the one you are given. Throughout this course we will assume you are `irods-user1`. 

We can test whether we have done everything correctly and have access:

```py
coll = session.collections.get('/aliceZone/home/irods-user1')
print(coll.path)
print(coll.data_objects)
print(coll.subcollections)
```

So far no data is stored in your iRODS collection. Let us upload some data.

We will need our home collection more often as reference point, so let us store the collection path:

```py
iHome = coll.path
```

### Upload a data object
The preferred way to upload data to iRODS is a data object *put*. 

Now we create the logical path and upload the German version of Alice in wonderland to iRODS. Note, we will also ensure that a checksum is created and verified:

```py
import irods.keywords as kw
# options for storing the checksum in the iCAT and verification of the checksum upon upload
options = {kw.VERIFY_CHKSUM_KW: '', kw.REG_CHKSUM_KW: "regChksum"}
iPath = iHome+'/Alice-DE.txt'
session.data_objects.put('aliceInWonderland-DE.txt.utf-8', iPath, **options)
```
The object carries some vital system information, otherwise it is empty. 

```
obj = session.data_objects.get(iPath)
print("Name: ", obj.name)
print("Owner: ", obj.owner_name)
print("Size: ", obj.size)
print("Checksum:", obj.checksum)
print("Create: ", obj.create_time)
print("Modify: ", obj.modify_time)
print("Metadata: ", obj.metadata.items())
```

Less code to write to display the full object:
```
vars(obj)
```

**Remark**: iRODS stores times in UNIX [epoch](https://en.wikipedia.org/wiki/Unix_time) time, but the python client always returns times in UTC (2 hours behind our local time).

**Exercise** Try to put data to an undefined path or your neighbours home collection (spelling mistake ...).

You can also rename an iRODS data object or move it to a different collection:

```py
session.data_objects.move(obj.path, iHome + '/Alice.txt')
print(coll.data_objects)
```

**Exercise** What happens if you try to move a data object to an existing data object?

### Creating metadata
Working with metadata is not completely intuitive, you need a good understanding of python dictionaries and the iRODS python API classes *dataobject*, *collection*, *iRODSMetaData* and *iRODSMetaCollection*.

We start slowly with first creating some metadata for our data. 
Currently, our data object does not carry any user-defined metadata:

```py
iPath = iHome + '/Alice.txt'
obj = session.data_objects.get(iPath)
print(obj.metadata.items())
```

Create a key, value, unit entry for our data object:

```py
obj.metadata.add('SOURCE', 'python API training', 'version 1')
obj.metadata.add('TYPE', 'test file')
```
If you now print the metadata again, you will see a cryptic list:

```py
print(obj.metadata.items())
```
The list contains two metadata python objects.
To work with the metadata you need to iterate over them and extract the AVU triples:

```py
[(item.name, item.value, item.units) for item in obj.metadata.items()]
```
Metadata can be used to search for your own data but also for data that someone shared with you. You do not need to know the exact iRODS logical path to retrieve the file, you can search for data wich is annotated accordingly. We will see that in the next section.

<!--
**Watch out:** If you do another `data_object.put` you will overwrite not only the bitstream but also all metadata. User-defined metadata will be set to empty.
-->

### Download a data object
We can download a data object as follows (note that we use the environment variable 'HOME' that is defined to be your homefolder):

```py
import os
options = {kw.VERIFY_CHKSUM_KW: ''}
localpath = os.environ['HOME']+'/'+os.path.basename(obj.path)
obj = session.data_objects.get(obj.path,local_path=localpath, **options)
```

**Exercise** Calculate the MD5 checksum for the downloaded data and compare with the data object's checksum in iRODS. (hint: `import hashlib; hashlib.md5(open(<filename>, 'rb').read()).hexdigest()`

### Streaming data
Streaming data is an alternative to upload large data to iRODS or to accumulate data in a data object over time. First you need to create an empty data object in iRODS beofre you can stream in the data.

```py
content = 'My contents!'.encode()
obj = session.data_objects.create(iHome + '/stream.txt')
```
This will create a place holder for the data object with no further metadata:

```py
print("Name: ", obj.name)
print("Owner: ", obj.owner_name)
print("Size: ", obj.size)
print("Checksum:", obj.checksum)
print("Create: ", obj.create_time)
print("Modify: ", obj.modify_time)
print("Metadata: ", obj.metadata.items())
```

```
vars(obj)
```
We can now stream in our data into that placeholder

```py
with obj.open('w') as obj_desc:
    obj_desc.write(content)
obj = session.data_objects.get(iHome + '/stream.txt')
```

Now we check the metadata again:

```py
print("Name: ", obj.name)
print("Owner: ", obj.owner_name)
print("Size: ", obj.size)
print("Checksum:", obj.checksum)
print("Create: ", obj.create_time)
print("Modify: ", obj.modify_time)
print("Metadata: ", obj.metadata.items())
```
```
vars(obj)
```

### Deleting data

With the python API you can only unlink data:

```py
obj.unlink()
```

This will move the data object to its respective location under */zone/trash/home/user/obj* but it will not remove the data from the iRODS instance and will also not clean up the data storage and metadata entries.

## iRODS collections

You can organise your data in iRODS just like on a POSIX file system.


### Create a collection (even recursively)
```py
session.collections.create(iHome + '/Books/Alice')
```
And test:

```
coll.path
coll.subcollections
```
**Exercise** Now we can move the Alice in Wonderland text in that collection.

 ```py
coll = session.collections.get(iHome + '/Books/Alice')
coll.data_objects
session.data_objects.move(iHome + '/Alice.txt', coll.path)
coll.data_objects
 ```
### Move a collection
Just as data objects you can also move and rename collections with all their data objects and subcollections:

```py
session.collections.move(iHome + '/Books', iHome + '/MyBooks')
coll = session.collections.get(iHome)
coll.subcollections
```

```
[vars(c) for c in coll.subcollections]
```
### Remove a Collection
Remove a collection recursively with all data objects.

```py
coll = session.collections.get(iHome + '/MyBooks')
coll.remove(recurse=True)
```
Do not be fooled, the python object 'coll' looks like as if the collection is still in iRODS. You need to refetch the collection (refresh).

```py
coll = session.collections.get(iHome)
coll.subcollections
```
```
[vars(c) for c in coll.subcollections] 
```

**Exercise** Create a collection, add some data to the collection and add some metadata to the collection (analogously to data object metadata).

### Upload collection
To upload a collection from the unix file system one has to iterate over the directory and create collections and data objects.
We will upload the directory 'aliceInWonderland'

```py
import os
dPath = os.environ['HOME']+'<path>'+'/aliceInWonderland'
walk = [dPath]
while len(walk) > 0:
    for srcDir, dirs, files in os.walk(walk.pop()):
        print(srcDir, dirs, files)
        walk.extend(dirs)
        iPath = iHome + srcDir.split(os.environ['HOME'])[1]
        print("CREATE", iPath)
        newColl = session.collections.create(iPath)
        for fname in files:
            print("CREATE", newColl.path+'/'+fname)
            session.data_objects.put(srcDir+'/'+fname, newColl.path+'/'+fname)
```

### Iterate over collection
Similar to we walked over a directory with sub directories and files in the unix file system we can walk over collections and subcollections in iRODS. Here we walk over the whole aliceInWonderland collection and list Collections and Data objects:

```sh
for srcColl, colls, objs in coll.walk():
    print('C-', srcColl.path)
    for o in objs:
        print(o.name)
```

## Sharing data
You can set ACLs on data objects and collections in iRODS. 
To check the default ACLs do:

```py
print(session.permissions.get(coll))
print(session.permissions.get(obj))
```

```
[vars(p) for p in session.permissions.get(coll)]
```
Here we share a collection with the iRODS group public. Every member of the group will have read rights.

```py
from irods.access import iRODSAccess
acl = iRODSAccess('read', coll.path, 'public', session.zone)
session.permissions.set(acl)
print(session.permissions.get(coll))
```

To withdraw certain ACLs do:

```sh
acl = iRODSAccess('null', coll.path, 'public', session.zone)
session.permissions.set(acl)
print(session.permissions.get(coll))
```

One can also give 'write' access or set the 'own'ership.

Collections have a special ACL, the 'inherit' ACL. If 'inherit' is set, all subcollections and data objects will inherit their ACLs from their parent collection automatically.

## Searching for data in iRODS
We will now try to find all data in this iRODS instance we have access to and which carries the key *AUTHOR* with value *Lewis Carroll*. And we need to assemble the iRODS logical path.

```py
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta
```
We need the collection name and data object name of the data objects. This command will give us all data objects we have access to:

```py
query = session.query(Collection.name, DataObject.name)
```
Now we can filter the results for data objects which carry a user-defined metadata item with name 'AUTHOR' and value 'Lewis Carroll'. To this end we have to chain two filters:

```py
filteredQuery = query.filter(DataObjectMeta.name == 'AUTHOR').\
    filter(DataObjectMeta.value == 'Lewis Carroll')
print(filteredQuery.all())
```

Python prints the results neatly on the prompt, however to extract the information and parsing it to other functions is pretty complicated. Every entry you see in the output is not a string, but actually a python object with many functions. That gives you the advantage to link the output to the rows and comlumns in the sql database running in the background of iRODS. For normal user interaction, however, it needs some explanation and help.

### Parsing the iquest output
To work with the results of the query, we need to get them in an iterable format:

```py
results = filteredQuery.get_results()
```
**Watch out**: *results* is a generator which you can only use once to iterate over.

We can now iterate over the results and build our iRODS paths (*COLL_NAME/DATA_NAME*) of the data files:

```py
iPaths = []

for item in results:
    for k in item.keys():
        if k.icat_key == 'DATA_NAME':
            name = item[k]
        elif k.icat_key == 'COLL_NAME':
            coll = item[k]
        else:
            continue
    iPaths.append(coll+'/'+name)
print('\n'.join(iPaths))
```

How did we know which keys to use? 
We asked in the query for *Collection.name* and *DataObject.name*.
Have look at these two objects:

```py
from pprint import pprint
pprint(vars(Collection))
print(Collection.name.icat_key)
pprint(vars(DataObject))
print(DataObject.name.icat_key)
```
The *icat_key* is the keyword used in the database behind iRODS to store the information.

**Exercise** What is the database key for a data object's checksum and its size? 

**Exercise** How would you retrieve files labeled with the 'AUTHOR' 'Lewis Carroll' list their checksum and determine their size?

**Solution**
The class *DataObject* carries an attribute *checksum*

```py
DataObject.checksum
```
which we can use in the query:

```py
query = session.query(Collection.name, 
    DataObject.name, 
    DataObject.checksum, 
    DataObject.size, 
    DataObjectMeta.value)
					  
filteredQuery = query.filter(DataObjectMeta.name == 'AUTHOR').\
    filter(DataObjectMeta.value == 'Lewis Carroll')
print(filteredQuery.all())
```
Metadata that the user creates with *obj.metadata.add* or *coll.metadata.add* are accessible via *DataObjectMeta* or *CollectionMeta* respectively. Other metadata is directly stored as attributes in *Collection* or *DataObject*.

## Putting it all together

1. Search for all data in the iRODS instance by the author Lewis Carroll.
2. Create an own collection in your iRODS home collection.
3. Copy (`session.data_objects.copy()`) the data objects to the new collection without downloading and uploading them.
4. Verify the checksums.
5. Open the collection to your neighbour by giving read rights.
