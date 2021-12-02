# Installation of iRODS resource server

This document describes how to install an resource server for iRODS4.2 on a Ubuntu machine. This iRODS instance does not come with an own database but will be connected to another iRODS server's iCAT database and by this become part of that iRODS zone.

## Environment

The documentation is tested with an Ubuntu 16.04 and Ubuntu 18.04 server.

## Prerequisites

You need another iCAT iRODS server.

### 1. Add repo key, Update and upgrade if necessary

#### Ubuntu16

```sh
wget -qO - https://packages.irods.org/irods-signing-key.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.irods.org/apt/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/renci-irods.list
sudo apt-get update
```

#### Ubuntu18

1. install postgresql
2. edit  /etc/apt/sources.list.d/renci-irods.list

```sh
deb [arch=amd64] https://packages.irods.org/apt/ xenial main
```

3. `sudo apt-get update`

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

## Installing iRODS

**Note**: You are installing here a "consumer" iRODS instance

### Install iRODS packages

```sh
sudo apt-get install irods-server
```

### Configuring iRODS as a resource server

```sh
sudo python /var/lib/irods/scripts/setup_irods.py
```

Configuration:

```
iRODS server's role:
1. provider
2. consumer
Please select a number or choose 0 to enter a new value [1]: 2
```

Use the zone name of the iCAT enabled instance

```
iRODS server's zone name [tempZone]: aliceZone
iRODS catalog (ICAT) host: <IP address of iCAT enabled host>
iRODS server's administrator username [rods]: <iadmin of iCAT enabled host>
```

### Test

If all went well, go to your irods iCAT enabled instance and do:

```
ilsresc
```

You should find a new resource `<servername>Resc` and if you zoom into that resource

```
ilsresc <servername>Resource -l
```

You should see that the resource is located on the resource server, e.g.

```
resource name: remoteResource
id: 10050
zone: aliceZone
type: unixfilesystem
class: cache
location: <IP or FQDN>
vault: /var/lib/irods/Vault
free space: 
free space time: : Never
status: 
info: 
comment: 
create time: 01586343758: 2020-04-08.11:02:38
modify time: 01586343758: 2020-04-08.11:02:38
context: 
parent: 
parent context: 

```

## Creating resources for another iRODS server

Now you can go ahead and create resources on the resource server. Here an example.

1. On the resource server create folders for iRODS resources

```
sudo mkdir -p /data/iRODSrescoures/offSite1
sudo mkdir -p /data/iRODSrescoures/offSite2
sudo chown -R irods:irods /data/iRODSrescoures
```

2. On the iRODS iCAT enabled server (here alice) do

```
iadmin mkresc remoteResc1 unixfilesystem <fqdn resource server>:/data/iRODSrescoures/offSite1
 iadmin mkresc remoteResc1 unixfilesystem <fqdn resource server>:/data/iRODSrescoures/offSite2
```

3. Now you can combine local and remote resources in coordinating resources like a replication resource

```
iadmin addchildtoresc twiceasmuch remoteResc2
```

4. Put some data into a remote resource

```
iput testfile.txt -R remoteResc1

ils -L testfile.txt 
  alice             0 remoteResc1           11 2020-04-08.11:38 & testfile.txt
        generic    /data/iRODSrescoures/offSite1/home/alice/testfile.txt

```

​		Now you can go to the resource server and check whether the file is really located in the reported path.



Full resource tree example:

```
ilsresc

aliceResc:unixfilesystem
demoResc:unixfilesystem
remoteResc1:unixfilesystem
resc4:unixfilesystem
robin:roundrobin
├── resc1:unixfilesystem
└── resc2:unixfilesystem
remoteResource:unixfilesystem
twiceasmuch:replication
├── remoteResc2:unixfilesystem
└── resc3:unixfilesystem

```

## Notes
You might have to edit the `/etc/irods/hosts_config.json` and make the resource server known to the iCAT-enabled server and vice-versa.
