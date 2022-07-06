# Fuji

### s3cmd

- Config

```
cat .s3cfg
access_key = <blablabla>
secret_key = <bla>
host_base = <hostname.or.ip>
host_bucket = <hostname.or.ip/bucketname>
signature_v2 = False
check_ssl_certificate = True
check_ssl_hostname = True
```



- Get status of file

```
staig001@scomp1447:~$ s3cmd info -d s3://irods/home/alice/testdata/data1GB.img
<snip>
'x-amz-restore': 'ongoing-request="false", expiry-date="Fri, 13 '
                              'May 2022 00:00:00 GMT"',
<snip>
```



- Stage data

```
s3cmd restore --no-check-certificate s3://irods/home/alice/testdata/data3GB.img
```



- Get status again

```
{'data': b'',
 'headers': {'accept-ranges': 'bytes',
             'connection': 'keep-alive',
             'content-length': '3221225472',
             'content-type': 'application/octet-stream',
             'date': 'Fri, 13 May 2022 11:18:12 GMT',
             'etag': '"2ded7487efa6fa479558ae7215c8177d-48"',
             'last-modified': 'Fri, 13 May 2022 11:18:00 GMT',
             'server': 'nginx/1.14.1',
             'x-amz-id-2': '40dba94a0347b9fd2964',
             'x-amz-request-id': '40dba94a0347b9fd2964',
             'x-amz-restore': 'ongoing-request="false", expiry-date="Sun, 15 '
                              'May 2022 00:00:00 GMT"',
             'x-amz-storage-class': 'GLACIER',
             'x-amz-version-id': '393833343832353535323432313539393939393952473030312020343134342e31393737373231'},
 'reason': 'OK',
```

## Streaming and downloading obj from glacier

If the data is stored on Glacier and not in the cache you will receive the following errors

#### Python API

Streaming

```
with irodsObj.open('r') as streaming:
	streaming.read()
S3_GET_ERROR: None
```

Downloading

```
irodsObj = session.data_objects.get("/aliceZone/home/alice/testdata/data3GB.img", local_path = "/home/christine/test")
SYS_FILE_DESC_OUT_OF_RANGE: None
```

### icommands

```
!iget /aliceZone/home/alice/testdata/data3GB.img
remote addresses: 10.90.2.49 ERROR: rcPartialDataGet: toGet 41943040, bytesRead 24 status = -27000 SYS_COPY_LEN_ERR
remote addresses: 10.90.2.49 ERROR: getUtil: get error for ./data3GB.img status = -27000 SYS_COPY_LEN_ERR
```

### Selecting a replica on a storage system

```python
obj.replicas #list of replicas and their storage system
replica = [o for o in obj.replicas if o.resource_name == '<irods resource>']
```

