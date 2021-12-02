# Federation between YODA and a plain iRODS instance
In this tutorial we will show how to federate the iRODS instance behind a YODA instance and a plain iRODS instance. 

## Prerequisites
- A YODA instance running on Centos
- An iRODS instance (4.2.8) on Ubuntu18; if you are working with real SSL certificates you can also run iRODS on a Centos machine

## Test instances

### Prepare YODA certificates

YODA test instances come with a self signed certificate. Those certificates are not automatically trusted by an Ubuntu server and hence not by an iRODS instance running on Ubuntu. We need to install YODA with certificates that are signed with the Ubuntu snakeoil CA.

1. Copy the folder [yoda-certs](yoda-certs) to your YODA machine
2. Do

```
sudo su
cd yoda-certs
update-ca-trust force-enable

#Install root CA
cp wurtest.crt /etc/pki/ca-trust/source/anchors
update-ca-trust extract

# install irods/httpd certificates
cp wurtest.crt /etc/pki/tls/certs/chain.crt
cp yoda.crt /etc/pki/tls/certs/localhost.crt
cat yoda.crt wurtest.crt > /etc/pki/tls/certs/localhost_and_chain.crt

# update the yoda keys
cp yoda.key /etc/pki/tls/private/localhost.key 
cp yoda.key /etc/irods/localhost.key

```

3. Restart the httpd service

   ```
   systemctl restart httpd
   exit
   ```

   

4. Restart iRODS

   ```
   sudo su - irods
   ./irodsctl restart
   ils
   exit
   ```

### Prepare iRODS certificates

Now we need to install the root CA on the Ubuntu server that hosts the iRODS instance

1. Copy the folder [yoda-certs](yoda-certs) to the machine

2. Do

   ```
   sudo su
   cd yodat-certs
   cp wurtest.crt /etc/ssl/certs
   cd /etc/ssl/certs
   ln -s wurtest.crt `openssl x509 -noout -hash < wurtest.crt`.0
   ```

3. Install irods certificates on iRODS server. We prepared valid certificates for testing in the folder [irods-certs](irods-certs). To use them you need to set the `/etc/hosts`

   ```
   127.0.0.1 irods.test
   127.0.0.1 localhost
   <snip>
   ```

4. Follow the steps in [10-SSL-encryption-and-PAM.md](10-SSL-encryption-and-PAM.md) to setup the SSL encryption (PAM not necessary) with these irods certificates.

## Create remote zone for YODA on iRODS server

Make sure your YODA zone and iRODS zone are called differently.

Ont he iRODS server do:

```
iadmin mkzone <yodaZone> remote <full hostname or ipadress of bob>:1247
iadmin mkuser rods#<yodaZone> rodsuser
```

Edit the `/etc/irods/server_config` as in [02-iRODS-federation](02-iRODS-federation.md).

On YODA do:

```
iadmin mkzone <irodsZone> remote <full hostname or ipadress of bob>:1247
iadmin mkuser rods#<yodaZone> rodsuser
```

Edit the `/etc/irods/server_config`.

Note that your remote iRODS user doe snot have a home in YODA. You need to add the user to a group.

### Known issues
As user from the native iRODS instance you cannot put, get or irsync data to YODA. 
https://github.com/UtrechtUniversity/yoda/issues/82 

### TODO

How to enable remote users through the YODA layer?
