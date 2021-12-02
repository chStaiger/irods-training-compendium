# iRODS advanced User Training

- Recap on icommands
- iRODS storage resources and implicit data policies
- iRODS rule language and write your own backup data policy

## Recap icommands (15 min)

Command 	| Meaning
---------|--------
iinit		| Login
ienv		| iRODS environment
iuserinfo	| User attributes
**ihelp**		| List of all commands
**\<command\> -h** | Help
**Up- and down load**	|
iput	[-K -r -f -R \<resc\>]	| Upload data, create checksum, recursively, overwrite, specify resource
iget [-K -r -f]	| Check checksum, recursively, overwrite
**Data organisation** |
ils [-L -A -l] | List collection [Long format, Accessions, less long format]
imkdir		| Create collection
icd			| Change current working collection
**Replica handling** |
irepl [-R \<resc\> -a -r]| Replicate btstreamn to another resource
itrim [-n -N -r]| Trim the number of replicas
**System Metadata** | 
ilsresc [-z \<zone name\> -l] | List all storage resource
**Synchronisation** |
irsync [-r -l] | Synchronise data between client and iRODS zone or between iRODS zones
**iRODS rules** |
irule [-F -v]   | Execute a rule
**Metadata** 		|
imeta add [-d -C] Name AttName AttValue [AttUnits]	| Create metadata [file, collection]
imeta ls [-d -C]	| List metadata [file, collection]
iquest		| Find data by query on metadata
iquest attrs	| List of attributes to query 

**Some predefined attributes for iquest:**

USER\_ID, USER\_NAME, RESC\_ID, RESC\_NAME, RESC\_TYPE\_NAME, RESC\_CHILDREN, RESC\_PARENT, DATA\_NAME, DATA\_REPL\_NUM, DATA\_SIZE, DATA\_RESC\_NAME, DATA\_PATH, DATA\_OWNER\_NAME, DATA\_CHECKSUM, COLL\_ID, COLL\_NAME, COLL\_PARENT\_NAME, COLL\_OWNER,\_NAME META\_DATA\_ATTR\_NAME, META\_DATA\_ATTR\_VALUE, META\_DATA\_ATTR\_UNITS, META\_DATA\_ATTR\_ID, META\_COLL\_ATTR\_NAME, META\_COLL\_ATTR\_VALUE, META\_COLL\_ATTR\_UNITS, META\_COLL\_ATTR\_ID, META\_COLL\_CREATE\_TIME, META\_COLL\_MODIFY\_TIME, META\_NAMESPACE\_COLL, META\_RESC\_ATTR\_NAME, META\_RESC\_ATTR\_VALUE, META\_RESC\_ATTR\_UNITS

**Example query**:

```
iquest "select COLL_NAME, DATA_NAME, META_DATA_ATTR_VALUE where \
META_DATA_ATTR_NAME like 'AUTHOR' and META_DATA_ATTR_VALUE like '%Arthur%'"
```

Remember: '%' is a wildcard in iquest.

### Login
You login to iRODS with the command

```
iinit
```
You will be asked for the iRODS server you would like to connect to the port (standard 1247), the zone name of the iRODS server, your iRODS user name and password.

**NOTE: Adjusting the default checksum (needed for exercises with checksum checking)**

Since iRODS 4.2.0 users need to adjust the default hash scheme for checksums if they want to use MD5 instead of SHA256.

Open the environment file:

```sh
vi .irods/irods_environment.json
```

And insert at the top:

```sh
    "irods_default_hash_scheme": "MD5",
```

### Basic commands
First we will have a look at some very basic commands to move through the logical namespace in iRPDS. The basic commands in iRODS are very similar to bash/shell commands.
You can browse through your coollections with:

```
ils
```
And you can create new collections with:

```
imkdir lewiscarroll
```

### Uploading data to iRODS
We can put a single file into our home-collection or a designated collection.

```
iput -K aliceInWonderland-DE.txt.utf-8
```
The flag *-K* triggers the calculation and verification of a checksum, in this case an md5 sum or digest of the sha256 checksum. 
Now upload a collection to iRODS:

```
iput -r -K aliceInWonderland lewiscarroll/alice
```
The option *K* triggers the calculation of checksums and verifies them upon upload.

### Logical and physical namespaces in iRODS
The *ils* command gives you an option to extract the physical location of a file:

```
ils -L -r lewiscarroll/alice
```

You will see some output like:

```
/aliceZone/home/irods-user1/lewiscarroll/Alice:
  irods-user1       0 demoResc       109858 2018-01-03.09:43 
  & aliceInWonderland-EN.txt.utf-8 4469a7b948107c7d5bba84b0403cd415   
  generic    
  /var/lib/irods/Vault/home/irods-user1/lewiscarroll/Alice/aliceInWonderland-EN.txt.utf-8
```

We will use this command quite often today to see what happens with files upon replication.
With this command you see where the file is stored on the iRODS server.

- *alice* is the data owner
- *0* is the index of this replica. the number only refers to replicas in one iRODS zone and can be used to automatically trim the number of replicas or create new ones in case one got lost.
- *demoResc* is the resource on which the data is stored. Resources can refer to certain paths on the iRODS server or other storage servers and clusters.
* The next entry is the time of the upload and the file name
* The '&' indicates that the checksum was successfully veryfied
* The follwing entry is the checksum
* The last entry is the physical path of the data, in our case the data lies on the iRODS server.

### Exercise (5 min)

Data can be downloaded from iRODS to your local machine with the command *iget*.
Explore the command *iget* to **store the data in your home directory**. Do **not overwrite** your original data and **verify checksums**!

## iRODS resources (30 minutes)
(Note: commands and resource hierarchies are still todo)

With the command `ils -L` we explored the link between the iRODS logical namespace and the the physical location of files and folders. The same can be done with resources.

iRODS resources are pieces of a file system, external servers or software in which data can be stored.

You can list all resources you have available with:

```
ilsresc
```
You will see the resource tree.

```
aliceResc:unixfilesystem
demoResc:unixfilesystem
robin:roundrobin
├── resc1:unixfilesystem
└── resc2:unixfilesystem
scomp1446R:unixfilesystem
twiceasmuch:replication
├── resc3:unixfilesystem
└── resc4:unixfilesystem
```
There are the storage resources: demoResc, twiceasmuch, resc1-4, robin, ...

The resources demoResc, aliceResc and scomp1446R can be used directly to store data.
The resources resc1-4 are managed by coordinating resources

If not further specified all your data will go to 'demoResc'.

You can specify the resource on which your data shall be stored directly with the put command. Let us put some data on aliceResc resource.

We first create a *test.txt*

```
echo "Some test text" > test.txt
```

```
iput -K -R aliceResc test.txt testfile-on-alice.txt
```

BIG advantage: As a user you do not need to know which storage medium is hidden behind the resource, you simply use the 
icommands to steer your data movements in the backend.

### User-defined replication of data (bit streams)
Once your data is lying in iRODS you can also replicate your data to another predefined resource.
Use `irepl` to replicate the German version of Alice in Wonderland to aliceResc

```
irepl -R aliceResc aliceInWonderland-DE.txt.utf-8
```

```
ils -l aliceInWonderland-DE.txt.utf-8
  irods-user1       0 demoResc           28 2020-10-12.12:36 & aliceInWonderland-DE.txt.utf-8
  irods-user1       1 aliceResc           28 2020-10-12.12:44 & aliceInWonderland-DE.txt.utf-8

```

The replicas are enumerated. With this number you can specifically remove a replica. Let us remove the replica on the demoResc:

```
itrim -n 0 aliceInWonderland-DE.txt.utf-8
```
We still have a copy of the English version in our system, so the logical name still exists:

```
ils -l aliceInWonderland-DE.txt.utf-8
  irods-user1       1 aliceResc           28 2020-10-12.12:44 & aliceInWonderland-DE.txt.utf-8
```

If you do an 

```
irm aliceInWonderland-EN.txt.utf-8
```
the whole data object, metadata and all replicas, will be removed. 

### Small exercise
1. Replicate a file to two different resources
3. What happens if you want to store data on resc1?
2. Explore `itrim` and trim the number of replicas to 1 (1 original and 1 replica)

### Summary so far

- Child resources cannot be accessed directly
- Replicas are numbered sequentially, new replica always receives the successor of the highest index
- Note the difference between the option -n and -N!
- When trimming replicas to a specific number, the replicas with the highest indexes are removed
- **Watch out**: replicas are not automatically updated (no automatic synchronisation). If you overwrote a replica the '&' sign in the listing will disappear for all other replicas. You can trigger the update with `irepl -a <irods path>`

### Resources have a life of their own (Low-level data policies)
In iRODS the system admin can group resources and enforce certain data replication or copying policies.

```
iput -K -R robin test.txt testfile-on-rr.txt
ils -l testfile-on-rr.txt
```

### Small exercise
- Where is your data stored physically. 
- Where is your neighbours data stored?
- Upload several files after each other. Where does the data land physically?

## Exercise: Explore the data policy behind twiceasmuch (20min)

We have seen that a round robin implements a certain data policy. Which data policy is hidden behind 'twiceasmuch'?

1. Consider putting data and trimming data.

**Note** As an iRODS user you do not need to know which servers and storage systems are involved. 
You only need an idea about the policies hidden behind grouped resources.

## Exercise: Where is the test file we put on 'scomp1446R' physically located? (10min)
Hints: 

1. You need to combine information from the iRODS system and the linux file system.
2. Where are all the resources located? (`ilsresc -l`)
3. How many servers does the iRODS system use?

## iRODS rules (30min)
In the previous parts we did a lot of work manually:

- replicating data to a different zone
- labeling data to keep track of originals and replicas

iRODS offers the possibility to automate data management processes by creating scripts written in the iRODS rule language. We will first inspect the iRODS rule language and then automatise the steps of the previous section and finally schedule the backup process in regular time intervals.

Save the example rule below in a file called *helloworld.r*

```
HelloWorld{
	writeLine("stdout", "Hello *name!");
}

INPUT *name="YourName"
OUTPUT ruleExecOut, *name
```

and execute the rule with

```sh
irule -F exampleRules/helloworld.r
```

### Passing arguments, variables and ouput
The rule has an input variable which we did not set in the previous call. The default value for the variable is "YourName".
To customise the function, we could alter the code, or we could pass on the right value for the variable.

```
HelloWorld{
	writeLine("stdout", "Hello *name!");
}

INPUT *name="YourName"
OUTPUT ruleExecOut, *name
```

We can overwrite input parameters by calling the function like this:

```sh
irule -F exampleRules/helloworld.r "*name='Alice'"
```

### Exercise: Passing variables, data types (10min)

```
variables{
	writeLine("stdout", "var1 is *var1!");
	writeLine("stdout", "var2 is *var2!");
}

INPUT *var1=1, *var2="string"
OUTPUT ruleExecOut, *name
```

- Alter the type of the input variables: numbers and simple calculations, booleans (true, false), strings
- How do you only change one of the two variables?

```sh
irule -F exampleRules/variables.r '*var1="Hello"'
```

```sh
irule -F exampleRules/variables.r "*var1='456'" "*var2='true'"
```

```sh
irule -F exampleRules/variables.r '*var1=3+4/7.'
```

```sh
irule -F exampleRules/variables.r "*var1='Hello'" "*var2=Hello"
```

### Global/System variables

iRODS knows predefined global variables that are set by the system and can come in handy. Those variables are addressed by "$" just like in shell scripting.

```sh
$userNameClient
$rodsZoneClient
$objPath
```

With them you can e.g. create the home collection of the active user:

```sh
*home="/$rodsZoneClient/home/$userNameClient"
```

### Looping over collections

iRODS is a data management software. In most cases we would like to loop over data objects and collections.
This is a rule that lists all data objects in a user's 'home' collection.

```c
recursivelist{
    *home="/$rodsZoneClient/home/$userNameClient"
    writeLine("stdout",*home);
    foreach(*row in SELECT COLL_NAME, DATA_NAME WHERE COLL_NAME like '*home%'){
        *coll = *row.COLL_NAME;
        *data = *row.DATA_NAME;
        writeLine("stdout", "*coll/*data");
    }
}

input null
output ruleExecOut
```
```sh
irule -F exampleRules/recursivelist.r
```
The '%' works as wild card, variables are denoted by '*'.

We see that this kind of for-loops use statements similar to the ones in the *iquest* command to retrieve data and collections.

### Exercise (15min)
Write a rule that finds all data objects and all collections that carry the same metadata attribute.
E.g. there is a collection labeled with the attribute 'game' and there are some files carrying the same attribute. Make the attribute a variable.

### Solution framework

```c
queryall{
	foreach(*row in SELECT COLL_NAME, <FILL IN> where <FILL IN> like '*var'){
		*coll = *row.COLL_NAME;
       *value = *row.<FILLIN>;
       writeLine("stdout", "<Some output>");
   	}
   	foreach(*row in SELECT COLL_NAME, <FILL IN>, <FILL_IN> where <FILL IN> like '*var'){
		*coll = *row.COLL_NAME;
		*data = *row.<FILL IN>;
       *value = *row.<FILL IN>;
       writeLine("stdout", "<Some output>");
    }
}

input *var='game'
output ruleExecOut
```

### Solution

```c
queryall{
        foreach(*row in SELECT COLL_NAME, META_COLL_ATTR_VALUE 
        	where META_COLL_ATTR_NAME like '*var'){
        *coll = *row.COLL_NAME;
        *value = *row.META_COLL_ATTR_VALUE;
        writeLine("stdout", "*coll *value");
        }
        foreach(*row in SELECT COLL_NAME, DATA_NAME, META_DATA_ATTR_VALUE 
        	where META_DATA_ATTR_NAME like '*var'){
        *coll = *row.COLL_NAME;
        *data = *row.DATA_NAME;
        *value = *row.META_DATA_ATTR_VALUE;
        writeLine("stdout", "*coll/*data *value");
        }
}

input *var='Easter'
output ruleExecOut
```

### If-statements and on-statements

```c
conditionalhello{
    if(*name!="Your Name"){
        writeLine("stdout", "Hello *name!");
        }
    else { writeLine("stdout", "Hello world!"); }
}
INPUT *name="Your Name"
OUTPUT ruleExecOut, *name
```
```
irule -F exampleRules/conditionalhello.r "*name='You'"
```

iRODS knows another conditional structure, the on-statement. It can be seen as a *switch statement* in other programming languages.
The same rue above looks like this with on-statements:

```c
hellorule{
    *result = hello(*name);
    writeLine("stdout", "*result");
}

hello(*name){
    on(*name=="Your Name")
        { "Hello world!"; }
}

hello(*name){
    "Hello *name!";
}

INPUT *name="Your Name"
OUTPUT ruleExecOut, *name
```
```
irule -F exampleRules/conditionalhelloon.r
```

The *hello* rules implement single cases of data policies. The *hellorule* puts them together in a sort workflow.
iRODS executes the first *hello* rule that matches the input and leads to some action.

iRODS is a not a real programming language but a rule/policy language. Thus, rules should not be seen as functions but as policies. 

The rules work like a filter. Rules can have the same name and different bodies. The first rule that matches the parameters is executed. Hence, the most general rule (policy) should go to the back.

On-statements enable us to define different policies and update them without breaking other policies. Explore that in the exercise below.

### Exercise (15min)

- Write a rule with different cases (decision between data policies), set the variable "iresource" accordingly:
	- If the data size is large, "iresource" should be "archive"
	- If the data should be highly available, "iresouce" should be "replResc"
	- If the data is classified as sensitive data, "iresource" should always be "storage3"
	- In all other cases the data should go to the "demoResc"
	
- Implement the policies using *if* or *on*.
- Which of the two is more advantagous if you think of what you need to alter when one of the cases (policies) changes?
- Why would you put the cases tested with *on* in different rules (all carrying the same rule name)?

### Solution framework

```c
policydecision{
	# example if
	if(*size=="large"){* resourceName = "archive"}
	else{ ... }
	# example on
	*resourceName = storagepolicy(*size, *privacy, *availability)
	writeLine("stdout", "*resourceName")
}

#example on
storagepolicy(*size, *privacy, *availability){
	on(*availability=="high"){"replResc"}
}

INPUT *size=<FILL IN>, *privacy=<FILL IN>, *availability=<FILL_IN> 
OUTPUT ruleExecOut
```

### Solution with on

```c
policydecision{
        *resourceName = storagepolicy(*size, *privacy, *availability);
        writeLine("stdout", "*resourceName");
}

storagepolicy(*size, *privacy, *availability){
        on(*privacy=="high"){ "storage3"; }
}

storagepolicy(*size, *privacy, *availability){
        on(*availability=="high"){ "replResc"; }
}

storagepolicy(*size, *privacy, *availability){
        on(*size=="large"){ "archive"; }
}

storagepolicy(*size, *privacy, *availability){
        "demoResc";
}

INPUT *size="large", *privacy="low", *availability="high"
OUTPUT ruleExecOut
```
