# iRODS hands-on for admins
This tutorial explains how to administrate users and resources as irods admin.
We will work with the *icommands* installed on the user interface machine. You will need *irodsadmin* rights and *sudo* rights on the 
iRODS server (e.g. alice-server).

## The *iadmin* mode
Creating users and resources are done under the *iadmin* mode. You can enter this mode by typing
```sh
iadmin #start mode
help
q #quit mode
```
In this mode you can only execute iadmin commands listed under *help* but not the 'normal' icommands such as *iput*.
Alternatively, all iadmin commands can be executed directly on the shell predeeded with 'iadmin'.

```sh
iadmin help
```

## User admnistration with iadmin

**Exercise** Inspect the function *iadmin mkuser* and *iadmin moduser* and create a "rodsuser" and a "rodsadmin".

[]()  | []()
------|------
iadmin mkuser      | create a user
iadmin moduser     | modify user attributes
iadmin rmuser      | delete a user
iadmin mkgroup     | create group

## iRODS resources
In iRODS you can create so-called resources which correspond to different physical locations such as resource servers and storage devices.
There are two types of of resources, **coordinating** and **storage** resources. By combining them you can create large decision 
trees with storage resources as leaves and coordinating resources to decide where the data should go to.

Recall that with *ilsresc* you can list all existing resources in your iRODS zone.
Let's create a new resource in your home directory on **alice-server** (the server on which iRODS is installed). To this end we create a new directory called *newVault* and declare it as a 
new storage resource.

```sh
iadmin mkresc newResc unixfilesystem <fully qualified hostname>:/home/alice/newVault
```
Since iRODS is executed not as your local user but as *irods*, putting data into the resource located in your home directory will fail:

```
iput -R newResc put2.txt
ERROR: putUtil: put error for /alicetestZone/home/alice/put2.txt,
 status = -520013 status = -520013 UNIX_FILE_MKDIR_ERR, Permission denied
```

This can be helped by granting read and write access to the *irods* user.
Usually resources are created directly under */var/lib/irods*.

### Composable resource trees

We will now create a resource tree in which data will be replicated automatically between two resources.
When you are working on our training machines please create the resources in your home directory and set the read and write access for the *irods* user. If you are working on your own machine you can create the resources directly under */var/lib/irods* or somewhere higher up the directory tree.

**1. Create a the physical resource**
First we will create the physical locations for the resources on the iRODS server:
```sh
sudo mkdir /var/lib/irods/iRODS/storage1
sudo mkdir /var/lib/irods/iRODS/storage2
chown irods:irods /var/lib/irods/iRODS/storage*
```

**2. Create two unix file system resources**
Now we can include these two resources as storage resources in iRODS:
```sh
iadmin mkresc storage1 unixfilesystem <fully qualified hostname>:/var/lib/irods/iRODS/storage1
iadmin mkresc storage2 unixfilesystem <fully qualified hostname>:/var/lib/irods/iRODS/storage2
```
All iRODS users will have access to these two resources.

**3. Create a coordinating replication resource**
```sh
iadmin mkresc replResc replication
```
The keyword *replication* triggers the behaviour of this cordinating resource. All data in this resource will be automatically replicated between the two storage resources.

**4. Connect the resources**
```sh
iadmin addchildtoresc replResc storage1
iadmin addchildtoresc replResc storage2
```

We can inspect the resource tree and put data. Usually data is put into the coordinating resource, i.e. *replResc*.
From there the data replicated to the two leaves, *storage1* and *storage2*. 

```sh
ilsresc
iput -R replResc test.txt
```

```sh
ils -L put2.txt
  alice             0 replResc;storage2           13 2016-05-05.00:12 & put2.txt
        generic    /var/lib/irods/iRODS/storage2/home/alice/put2.txt
  alice             1 replResc;storage1           13 2016-05-05.00:12 & put2.txt
        generic    /var/lib/irods/iRODS/storage1/home/alice/put2.txt
```

Resource trees implement data policies on the system level. You can find a full list of preimplemented coordinating storage resources [here](https://docs.irods.org/master/plugins/composable_resources/#coordinating-resources)

[]()  | []()
------|------
iadmin mkresource  | create a resource
iadmin rmresc      | delete a resource
iadmn modresc     | modify resource attributes

### Exercises
1. Try to send data directly to *storage2* or *storage1*.
2. Modify the replication resource to the type *roundrobin* and test where newly ingested data will be saved. Hint: upload several files.

### Compound resources
Compound resources consist of a cache resource and an archive resource. Data is entered to the cache resource and passed later to the archive resource.
The archive resource can be of several storage types for which one might need to adapt the data transfer protocol. This is defined in */var/lib/irods/iRODS/server/bin/cmd/univMSSInterface.sh*

To create such a compound resource, please refer to this [setup](https://github.com/trel/irods-compound-resource/blob/master/SETUP.md).

*Exercise* Inspect the *univMSSInterface.sh* and adopt it to work with *rsync* or another transfer protocol.
