# iRODS instances setup

## Bob 

### Additional resource

```sh
sudo mkdir -p /data/irodsRescBob
sudo chown irods:irods /data/irodsRescBob
iadmin mkresc bobResc unixfilesystem <server>:/data/irodsRescBob
```

## Alice

### Additional resource

```sh
sudo mkdir -p /data/irodsRescAlice
sudo chown irods:irods /data/irodsRescAlice
iadmin mkresc aliceResc unixfilesystem <server>:/data/irodsRescAlice
```

### RoundRobin resource

Create folders

```sh
sudo mkdir /data/irodsResc1
sudo mkdir /data/irodsResc2
sudo chown irods:irods /data/irodsResc*
```

Add iRODS resources

```sh
iadmin mkresc resc1 unixfilesystem scomp1447:/data/irodsResc1
iadmin mkresc resc2 unixfilesystem scomp1447:/data/irodsResc2
```

Create roundrobin and add children resources

```sh
iadmin mkresc robin roundrobin
iadmin addchildtoresc robin resc1
iadmin addchildtoresc robin resc2
```

### Replication resource

Create folders

```sh
sudo mkdir /data/irodsResc3
sudo mkdir /data/irodsResc4
sudo chown irods:irods /data/irodsResc*
```

Add iRODS resources

```sh
iadmin mkresc resc3 unixfilesystem scomp1447:/data/irodsResc3
iadmin mkresc resc4 unixfilesystem scomp1447:/data/irodsResc4
```

Create replication resource and add children resources

```sh
iadmin mkresc twiceasmuch replication
iadmin addchildtoresc twiceasmuch resc3
iadmin addchildtoresc twiceasmuch resc4
```



### Metadata Game

Data and install information in folder `game`.



### Event hook

Create `/etc/hooks.re`

```
acPostProcForPut{
  ON($objPath like "/$rodsZoneClient/home/$userNameClient/event/*"){
    msiWriteRodsLog("LOGGING: object", *Status);
    msiWriteRodsLog("$objPath triggered event hook", *Status);
    msiAddKeyVal(*Keyval,"TRIGGER","acPostProcForPut");
    msiGetObjType($objPath, *objType);
    msiAssociateKeyValuePairsToObj(*Keyval,$objPath,*objType);
    msiWriteRodsLog("LOGGING END", *Status);
  }
}

acPostProcForPut { }

acPostProcForCollCreate{
  ON($collName like "/$rodsZoneClient/home/$userNameClient/event/*"){
    msiWriteRodsLog("LOGGING: Collection", *Status);
    msiWriteRodsLog("$collName triggered event hook", *Status);
    msiAddKeyVal(*Keyval,"TRIGGER","acPostProcForCollCreate");
    msiAssociateKeyValuePairsToObj(*Keyval,$collName,"-C");
    msiWriteRodsLog("LOGGING END", *Status);
  }
}

acPostProcForCollCreate { }
```

And configure rule base in `/etc/irods/server_config.json.`

 ```
"re_rulebase_set": ["core", "hooks"],
 ```



## iRODS userinterface machine setup

### ipython

- Install pip3

```sh
apt install python3-pip
pip3 --version

pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.6)
```

- Install ipython for python 3

```python
pip3 install ipython

ipython

Python 3.6.9 (default, Nov  7 2019, 10:44:02) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:              
```

### iRODS python API

```python
pip3 install python-irodsclient
ipython

Python 3.6.9 (default, Nov  7 2019, 10:44:02) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import irods  

```

### icommands

```sh
wget -qO - https://packages.irods.org/irods-signing-key.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.irods.org/apt/ xenial main" | sudo tee /etc/apt/sources.list.d/renci-irods.list
sudo apt-get update
sudo apt -y install aptitude irods-runtime=4.2.6 irods-icommands=4.2.6
```

## Users
### Alice
#### Create 25 iRODS test accounts
```
for i in {1..25}; do 
USER=irods-user${i}; 
echo $USER; 
iadmin mkuser $USER rodsuser; 
iadmin moduser $USER password $USER
done
```
#### Create training group
```
iadmin mkgroup training
for i in {1..25}; do 
USER = irods-user${i};
iadmin atg training $USER
done
```

### Bob
Allow the training users from alice to access bob:
On Bob do:
```
for i in {1..25}; do 
USER=irods-user${i}#aliceZone; 
echo $USER; 
iadmin mkuser $USER rodsuser; 
done
```







