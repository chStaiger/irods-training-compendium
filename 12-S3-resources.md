# 12-S3-resources

## Synopsis

Wageningen IT offers storage on Isilon to users. The current service comprises cifs and nfs mounts. Both can be integrated with iRODS by mounting the exported file systems to a linux machine and add the path of the mount as an unix file system storage resource. This way of offering storage to iRODS is very prone to connection errors and lacks also performance in terms of data transfer speed.

Isilon offers the S3 API as part of a Swift cluster. iRODS in turn has an S3 plugin with which iRODS can directly interact with an Amazon S3 or a Swift/Isilon storage system.

Here we describe the general setup, the current state of the PoC and future work.

## Setup

### Prerequisties

- For the setup you need access to an iRODS iCAT server or an iRODS resource server.
- You need an aws keypair and the name of the bucket on the Swift cluster
- Key Pair file

accesskey
accesskeysecret

### Configuration of the S3 resource in iRODS

1. On the respective server change to the iRODS service account (in most cases that is `irods`):

```
sudo su - irods
```

2. Create the resource:

```
iadmin mkresc s3resc s3 <fqdn_of_irods_server>:/irods "S3_DEFAULT_HOSTNAME=10.90.165.162:9020;S3_AUTH_FILE=/var/lib/irods/AWS.keypair;S3_RETRY_COUNT=1;S3_WAIT_TIME_SEC=3;S3_PROTO=HTTP;ARCHIVE_NAMING_POLICY=consistent;HOST_MODE=cacheless_attached"
```

`10.9 0.165.162:9020` is the HTTP endpoint of our local Isilon-Swift cluster (test instance) and `/irods`is the bucket name on the swift cluster.

3. Test the data upload with

```
ilsresc -l s3resc
iput -R s3resc test-file.txt
ils -l test-file.txt
```

### Current state

- In the current integration we are using HTTP instead of HTTPS. To make iRODS connect to the HTTPS endpoint, real certificates from a CA have to be installed.

### Next steps

- Investigate how to enable HTTPS
- Procedure how to deal out secret pairs and buckets

## Install certificates for S3 on Ubuntu

```
openssl x509 -inform PEM -in isilon99_wurnet_nl_interm.cer -out isilon99.crt
sudo cp isilon99.crt /usr/local/share/ca-certificates/extra
sudo update-ca-certificates 
```

