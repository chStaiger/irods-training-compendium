# Installation of iRODS 4.2

This document describes how to install iRODS4.2 on a Ubuntu machine with a postgresql database as iCAT.

## Environment

The documentation is tested with an Ubuntu 16.04 and Ubuntu 18.04 server.

## Prerequisites

### 1. Add repo key, Update and upgrade if necessary

#### Ubuntu16 and 18

```sh
wget -qO - https://packages.irods.org/irods-signing-key.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.irods.org/apt/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/renci-irods.list
sudo apt-get update
```

### 2. Set firewall

```sh
sudo apt-get install iptables-persistent
sudo service netfilter-persistent start
sudo invoke-rc.d netfilter-persistent save
sudo service netfilter-persistent stop

mkdir iptables-rules
```

- create  ~/iptables-rules/ruleset-v4 

```sh
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [4538:480396]
-A INPUT -m state --state INVALID -j DROP
-A INPUT -p tcp -m tcp ! --tcp-flags FIN,SYN,RST,ACK SYN -m state --state NEW -j DROP
-A INPUT -f -j DROP
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG NONE -j DROP
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG FIN,SYN,RST,PSH,ACK,URG -j DROP
-A INPUT -p icmp -m limit --limit 5/sec -j ACCEPT
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 1248 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 1247 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 20000:20199 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 4443 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 5432 -j ACCEPT
-A INPUT -j LOG
-A INPUT -j DROP
COMMIT
```

```sh
sudo iptables-restore < ~/iptables-rules/ruleset-v4 
sudo iptables -S
sudo dpkg-reconfigure iptables-persistent
```

### 3. Set host name

Example hosts-file:

```sh
127.0.0.1   localhost
127.0.1.1	alice-server
IPa.ddr.ess  alice.eudat-sara.vm.surfsara.nl alice-server
```

### 4. Install postgresql

```sh
sudo apt-get install postgresql
sudo pg_createcluster 10 main --start
```

## Installing iRODS

### 5. Configure and create postgresql database

```sh
sudo su - postgres
/usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/10/main -l logfile start
```

If necessary fix `locale` settings before proceeding.

```
psql
CREATE DATABASE "ICAT";
CREATE USER irods WITH PASSWORD 'irods';
GRANT ALL PRIVILEGES ON DATABASE "ICAT" to irods;
\q
exit
```

#### Known issues

If you encounter the error:

```sh
postgres@scomp1447:~$ psql
psql: could not connect to server: No such file or directory
	Is the server running locally and accepting
	connections on Unix domain socket "/var/run/postgresql/.s.PGSQL.5432"?

```

Then do:

```sh
sudo mkdir -p /var/lib/pgsql/data/
sudo chown -R postgres:postgres /var/lib/pgsql
sudo su - postgres
/usr/lib/postgresql/10/bin/initdb /var/lib/pgsql/data/pg_hba.conf
/usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/pgsql/data/pg_hba.conf -l logfile start
```

```sh
psql
CREATE DATABASE "ICAT";
CREATE USER irods WITH PASSWORD 'irods';
GRANT ALL PRIVILEGES ON DATABASE "ICAT" to irods;
\q
exit
```

### 6. Install iRODS packages

```sh
sudo apt-get install irods-server irods-database-plugin-postgres
```



### 7. Configuring iRODS

```
sudo python /var/lib/irods/scripts/setup_irods.py
```

Set the following variables

```
iRODS user [irods]: 
iRODS group [irods]: 

+--------------------------------+
| Setting up the service account |
+--------------------------------+

Existing Group Detected: irods
Existing Account Detected: irods
Setting owner of /var/lib/irods to irods:irods
Setting owner of /etc/irods to irods:irods
iRODS server's role:

1. provider

+-----------------------------------------+
| Configuring the database communications |
+-----------------------------------------+

You are configuring an iRODS database plugin. The iRODS server cannot be started until its database has been properly configured.

ODBC driver for postgres:

PostgreSQL ANSI

Database server's hostname or IP address []: localhost
Database server's port [5432]: 
Database name [ICAT]: 
Database username [irods]: 

-------------------------------------------

Database Type: postgres
ODBC Driver:   PostgreSQL ANSI
Database Host: localhost
Database Port: 5432
Database Name: ICAT

+--------------------------------+
| Configuring the server options |
+--------------------------------+

iRODS server's zone name [tempZone]: aliceZone
iRODS server's port [1247]: 
iRODS port range (begin) [20000]: 
iRODS port range (end) [20199]: 
Control Plane port [1248]: 
Schema Validation Base URI (or off) [file:///var/lib/irods/configuration_schemas]: 
iRODS server's administrator username [rods]: alice

-------------------------------------------

Zone name:                  aliceZone
iRODS server port:          1247
iRODS port range (begin):   20000
iRODS port range (end):     20199
Control plane port:         1248
Schema validation base URI: file:///var/lib/irods/configuration_schemas

iRODS server administrator: alice

Please confirm [yes]: 
iRODS server's zone key: ALICE_ZONE_KEY
iRODS server's negotiation key (32 characters): 
```

### 8. Login to iRODS

```sh
iinit
```

```sh
Enter the host name (DNS) of the server to connect to: localhost
Enter the port number: 1247
Enter your irods user name: alice
Enter your irods zone: aliceZone
```

- Test whether you can list your iRODS directory

```sh
ils
```

### iRODS resource configuration

We now configure another resource on the same server. We need to grant the user who runs iRODS (usually *irods*) read and write access:

```
sudo mkdir /irodsVault
sudo chown -R irods:irods /irodsVault
iadmin mkresc aliceResc unixfilesystem alice-server:/irodsVault
```

### System control

As user `irods` you can use the command `irodsctl`to retrieve status, start and stop the service.

```staig001@scomp1447:~$ sudo su irods
irods@scomp1447:/var/lib/irods/irodsctl status 
irodsServer :
  Process 21356
  Process 21357
irodsReServer :
  Process 21359
```

### Additional Server configuration

#### Logging
iRODS creates a lot of log files, which are not cleaned up automatically. To do so start a cron-job:

```
sudo vim /etc/cron.d/irods
```

Add

```
# cleanup old logfiles older than 14 days
11      1       *       *       *       root    find /var/lib/irods/iRODS/server/log/{re,rods}Log.* -mtime +14  -exec rm {} \;
```

to the file. 
Now *root* will delete all reLog and rodsLog files that are older than 14 days. The command will be executed everyday at 11.01am.

#### Pinning packages
To prevent automatic package updates of the iRODS server create the file `/etc/apt/preferences.d/irods` with:

```
Package: irods-dev
Pin: version 4.2.8
Pin-Priority: 999



Package: irods-server
Pin: version 4.2.8
Pin-Priority: 999



Package: irods-runtime
Pin: version 4.2.8
Pin-Priority: 999



Package: irods-icommands
Pin: version 4.2.8
Pin-Priority: 999
```

as content.
