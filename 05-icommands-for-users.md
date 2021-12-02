# iRODS for users

This tutorial introduces you to the basics what iRODS is and how you do simple data management tasks as a user. We will use the icommands - the commandline client to iRODS.

## Prerequisites
- A user account on an iRODS 4.[1,2].X system
- icommands client, [Installation](http://irods.org/download/)
- If you are following this training on a compute cluster like Anunna (WUR) or Lisa/Cartesius/Snellius (SURF) you will need to load the icommands module. Check for the module and load it: 
  ```sh
  [user@login0 ~]$ module avail | grep icommands
  irods-icommands/4.2.8-1                                        
  [user@login0 ~]$ module load irods-icommands/4.2.8-1 
  load irods-icommands 4.2.8-1 library and binaries.
  ```

### Connecting to the iRODS server
First we connect to an iRODS server and authenticate as iRODS user. The user account has to be created by the iRODS admin beforehand, see the following section [Part 02](https://github.com/EUDAT-Training/B2SAFE-B2STAGE-Training/blob/master/02-iRODS-handson-admin.md).

```sh
iinit
```
When you connect for the first time, you will receive this answer:

```sh 
One or more fields in your iRODS environment file   (irods_environment.json) are
missing; please enter them.
```
Usually iinit uses the irods_environment.json to retrieve information to which iRODS instance to connect to and which user to use. If the file is incomplete or has not yet been generated you will have to provide this information:

```sh
Enter the host name (DNS) of the server to connect to:  <ip adrdress or fully qualified hostname>
Enter the port number: 1247
Enter your irods user name: <irodsuser>
Enter your irods zone: <zonename>
```
The default port numer is 1247. The zone name, username and password will be provided by the iRODS admin.
You can revisit the file and configuration in *.irods/irods_environment.json*. If you want to login as another iRODS user you will have to alter this file.

### Some iRODS concepts
**iRODS zone**: always contains exactly one so-called iCAT catalogue, which is a database containing user information, the mapping from physical storage to iRODS logical path for data and which hosts metadata attached to data.

**Resources**: Software or Hardware system that stores data. The iRODS system abstracts from the hardware and software so that you, as a user, can put data into certain resources without specific knowledge on the protocols to use.

**iRODS collections**: As a user you have access to a collection, just as a home directory on a linux system. In this collection you can create subcollections and store data. You can retrieve and store data and collections by using the iRODS (logical) path. The iCAT catalogue will take care of the mapping to the actual physical path.

## iRODS session management and help

[]()  | []() 
------|------
iinit       | Log on
iexit full       | Log off
ienv        | Client settings
ihelp       | List of icommands
ipasswd     | Change iRODS password
iuserinfo   | User info
ierror      | Information on error code

The most important icommand will be:
```sh
ihelp
```
This will print out all commands the client knows.

You can retrieve help on any icommand with:

```sh
<command> -h
```
or
```sh
ihelp <command>
```

## Data up- and download
[]()  | []() 
------|------
iput       | Upload data to iRODS
iget       | Download data from iRODS to local file system

Let us first create a first test file in your linux home-directory.

```sh
nano test.txt

My first test file
```
We will now upload the file to iRODS

```sh
iput -K test.txt
```
The flag *-K* triggers iRODS to create a checksum and store this checksum in the iCAT metadata catalogue.

We can safely remove the file from our linux home directory:

```
rm test.txt
ls
```
since the file is present on the iRODS server:
```
ils

ubuntu@ubuntu:~$ ils
/aliceZone/home/\<user\>:
  test.txt
```
To restore the file (copy it from iRODS to your linux home) you can do:

```
iget -K test.txt test-restore.txt
```
We store the iRODS file *test.txt* in a new file called *test-restore.txt* in our linux home directory.
Here the flag *-K* triggers iRODS to verify the checksum.

The two commands also work for directories and collections, simply use the *-r* (for recursive) flag.

## Connection between iRODS logical namespace and physical location of the data
The file *test.txt* lies on the logical iRODS path */aliceZone/home/\<user\>/test.txt*. This path we can use to address the file.
We can find out where the file is actually stored:
```sh
ils -L
```

iRODS will give us the user, which resource it is stored on and as last information the physical path on the iRODS server.
```sh
\<user\>              0 demoResc      13 2017-02-22.12:40 & test.txt
4db84b43c8abd49beaf2254ad25b9e5a        generic    /irodsVault/home/rods/test.txt
```
- `/aliceZone/home/alice/put1.txt`: Logical path to the file as iRODS exposes it to the user
- `alice`: owner of the file
- `0`: Index of replica of that file in the iRODS system, in iRODS the same file can lie on different 
- `demoResc`: the name of the physical data resource, e.g. a unix folder
- `13`: File size in KB
- Date
- Checksum
- `/irodsVault/home/alice/put1.txt`: Physical path on the server that hosts iRODS, only the linux user "irods" who runs iRODS has access to that path.

All the information above is stored in the iCAT metadata catalogue and can also be retrieved in sql-like queries (see below).

## iRODS file organisation

[]()    | []()
--------|------
ils     | List collection
icd     | Change working collection
ipwd    | Current working collection
ilocate | Locate object
icp     | Creates a new copy of that object on the physical and logical namespace level, will not inherit any metadata.

How come that all our data automatically ended up in the iRODS collection */aliceZone/home/\<user\>*?
```sh
ipwd
```
tells you your current working collection, which is by default your home-collection. This path is taken as a prefix to any iRODS file or collection path you use if you do not provide the full iRODS path.

Let's create a subcollection. You may already know the UNIX command *mkdir*. iRODS uses a similar command and syntax for creating collections:
```sh
imkdir testData
```
Let us move our test file to the collection:
```sh
imv test.txt testData
```

We can change our current working collection to the newly created directory
```sh
icd testData
ipwd
```
Now the *ils* command will by default give you the content of *testData*.

We can change back to our home collection by
```sh
icd /aliceZone/home/\<user\>
```
or by
```sh
iexit
```

With 
```sh
ils -r
```
we can list all collections and subcollections in iRODS recursively.

### Removing data
To remove our test.txt from iRODS use

```sh
irm testData/test.txt
```
Let's inspect what happens.
If we list the content of our current working collection, we will not find the file, so it seems to be deleted. However, inspecting the *trash* folder, shows that only the file's physical and logical path was changed. This is what we call a soft delete.
```sh
ils -L /aliceZone/trash/home/alice
```
```sh
/aliceZone/trash/home/alice:
  alice             0 demoResc           13 2016-02-19.13:52 & put1.txt
    d6eb32081c822ed572b70567826d9d9d    generic    /irodsVault/trash/home/alice/put1.txt
  C- /aliceZone/trash/home/alice/Data
```
That means you can restore the file with the follwing commands.
```sh
imv /aliceZone/trash/home/alice/testData/put1.txt /aliceZone/home/alice/testData
```
*imv* can be used to move data and subcollections and to rename them.
```sh
imv /aliceZone/home/alice/testData/put1.txt /aliceZone/home/alice/testData/put2.txt
```

To remove the file completely from the system, you need to execute
```sh
irmtrash
```
This is called a hard delete. Now the file is removed from the system and from the iCAT catalogue.

### Accession control

[]()    | []()
--------|------
ils -A    | List collection and ACLs
ichmod     | Set read, write, own permissions; set inhertiance for collections
ipwd    | Current working collection
ilocate | Locate object

With the option *-A* we can list the accession control list of files and collections.
```sh 
ils -A
```
```
    /aliceZone/home/alice:
            ACL - alice#aliceZone:own
            Inheritance – Disabled
```
This tells us that /home/alice is only visible by the user *alice* and the irodsadmin, who has access to all data by default.

Let's create a subcollection, put some data into it and open the collection for the user *bob*

```sh
imkdir DataCollection
ichmod inherit DataCollection
ichmod read bob DataCollection
```
With *ichmod inherit* we assure that all data and subcollections in *DataCollection* will inherit their ACL from the parent collection. After that we grant read-access to another user in the iRODS system. Data tat was put into the collection before the *inherit* flag was set, will keep their original ACLs.

Check the ACL settings of the collection.
```sh
ils -A DataCollection
```
Now we put some data into the collection.
```sh
iput -K test-restore.txt DataCollection/test-share.txt
```
The file *test-share.txt* inhertited the ACLs from its parent collection.
Note that when you change the ACLs of the parent collection, the ACLs of all files and subcollections are not automatically updated!

Our user bob can now list the collection and read put1.txt.
```sh
bob@irods4:~$ ils /aliceZone/home/alice/DataCollection
/aliceZone/home/alice/DataCollection:
  test-share.txt
```
**Exercise** Give read and write access to test.txt to your neighbour.

**Important**: When giving access to files and subcollections, the parent collection needs also to be read or writeable.

## Annotating data and searching for data

iRODS provides the user with the possibility to create **A**ttribute **V**alue **U**nit triplets and store them with the data. The triplets are stored in the iCAT catalogue, which can be queried to identify and retrieve the correct objects.

We can store information e.g. on the creation data of a file
```sh
imeta add -d test.txt "Date" "Nov 2015"
```
Here we created an attribute with the name *Date* and gave it the value *Nov 2015*. The unit section is left empty.

We can also annotate a collection
```sh
imeta add -C DataCollection "Type" "Collection"
imeta add -C DataCollection "Date" "Nov 2015"
```
To list AVUs stored for a file use:
```sh
imeta ls -d put1.txt
imeta ls -C DataCollection
```

**Exercise** Add some metadata to one of your files to depict two authors you and "alice".

The imeta command also allows us to define simple queries.
```sh
imeta qu -d Date = "Nov 2015"
```
For more sophisticated sql-like queries we can use

```sh
iquest "select sum(DATA_SIZE), COLL_NAME where COLL_NAME like '/aliceZone/home/alice/Data%'"
```
This command sums the sizes of all data in each collection starting with *Data*. The command *iquest* already knows some keywords specific to the iRODS environment. You can list them with

```sh
iquest attrs
```

**Exercise** Use the *iquest* command to find all data and collections with an Attribute "DATE". List the object name and the value associated with "Date".

**Exercise** Select some data with *iquest* and inspect the difference between *DATA_NAME* and *DATA_PATH*. Which of the two is used where in the command `ils -L`? 


> ### Listing of physical storage resources (move to advanced user training)
> To see which physical resources are attached to the iRODS instance and what their logical names are, you can use:
> ```sh
> ilsresc –l 
> ```
> which will yield:
> ```
> resource name: demoResc
> id: 9101
> zone: aliceZone
> type: unixfilesystem
> class: cache
> location: iRODS4.alice
> vault: /irodsVault
> ```
> This command lists all resources defined in the iRODS zone and their type, i.e. there is one resource of type *unix file system*. The value after *vault* tells us where our data will be stored physically when added to the resource. *location* gives the server name of the resource, in this case it is the iRODS server itself. Check with:

> ```sh
> hostname
> ```
> on your shell.

> Old iRODS version 
> ```sh
> icp -f DataCollection/put1.txt put1.txt
> ichmod read bob put1.txt
> ```
> If user *bob* now tries to list or retrieve put1.txt in our home collection he will receive the follwing error, although the ACLs on the file itself have been set correctly.

> ```
> ERROR: lsUtil: srcPath /aliceZone/home/alice/put1.txt does not exist or user lacks access permission
> ```
> This is due to the fact, that *bob* has no read rights on the parent collection /aliceZone/home/
