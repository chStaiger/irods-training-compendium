# Install Davrods

## Installation without SSL certificates (not advised)

1. Download davrods from https://github.com/UtrechtUniversity/davrods

```
apt-get install apache2
#apt --fix-broken install
dpkg -i davrods-X.deb
```

2. If SELinux is running on machine do

```
setsebool -P httpd_can_network_connect true
```

3. The configuration files are in

```
ls /etc/apache2/sites-available/
```

4. Adjust the respective files `davrods-(anonymous-)vhost.conf`

```
a2enmod dav
a2enmod davrods
a2ensite davrods-(anonymous-)vhost
```

5. Remove the file `rm /etc/apache2/sites-enabled/000-default.conf`.

6. Remove the line 

```
"irods_client_server_negotiation": "request_server_negotiation",
```

​    from `/etc/apache2/irods/irods_environment.json`.

7. Restart the HTTP server

```
systemctl restart apache2
```

## Enabling the WebDav server with SSL encryption

To enable an existing Davrods installation with SSL to safely transfer data and passwords do:

1. Get certificates **or**
2. Create self-signed certificates: 

```
openssl req -x509 -nodes -days 4000 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt
```

3. Enable ssl in apache

```
a2enmod ssl
```

4. Edit the `davrods-vhost.conf`in `/etc/apache2/sites-enabled`

```
<VirtualHost *:443>
```

  Add the following lines after '\</Location>'

```
SSLEngine on
SSLCertificateFile /etc/ssl/certs/apache-selfsigned.crt
SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key
```

5. Check the apache configuration and restart the service

```
apache2ctl configtest
systemctl reload apache2
```

6. Redirect HTTP to HTTPS

​       Edit `/etc/apache2/sites-available/000-default.conf`

```
ServerName <fqdn or ip>
Redirect permanent / https://<fqdn or ip>
```

​     Enable the page with `a2ensite 000-default` and then reload Apache 

`systemctl reload apache2`.

# Adjustments to the configuration files if the iRODS server itself is also enabled with SSL-encryption

If your iRODS server also uses SSL encryption you need to adjust the */etc/apache2/irods/irods_environment.json*

```
{
    "irods_client_server_negotiation": "request_server_negotiation",
    "irods_client_server_policy": "CS_NEG_REQUIRE",
    "irods_ssl_certificate_chain_file": "/etc/irods/ssl/irods.crt",
    "irods_ssl_certificate_key_file": "/etc/irods/ssl/irods.key",
    "irods_ssl_dh_params_file": "/etc/irods/ssl/dhparams.pem",
    "irods_ssl_ca_certificate_file": "/etc/irods/ssl/irods.crt",
    "irods_ssl_verify_server": "cert",
    "irods_connection_pool_refresh_time_in_seconds": 300,
    "irods_cwd": "/elabZone/home/elab",
    "irods_default_hash_scheme": "SHA256",
    "irods_default_number_of_transfer_threads": 4,
    "irods_default_resource": "demoResc",
    "irods_encryption_algorithm": "AES-256-CBC",
    "irods_encryption_key_size": 32,
    "irods_encryption_num_hash_rounds": 16,
    "irods_encryption_salt_size": 8,
    "irods_home": "/<ZONE>/home/<RODSADMIN USER>",
    "irods_host": "<IP or FQDN as in certificate>",
    "irods_match_hash_policy": "compatible",
    "irods_maximum_size_for_single_buffer_in_megabytes": 32,
    "irods_port": 1247,
    "irods_server_control_plane_encryption_algorithm": "AES-256-CBC",
    "irods_server_control_plane_encryption_num_hash_rounds": 16,
    "irods_server_control_plane_key": "SERVER_negotiationcontrol_key",
    "irods_server_control_plane_port": 1248,
    "irods_transfer_buffer_size_for_parallel_transfer_in_megabytes": 4,
    "irods_user_name": "<RODSADMIN USER>",
    "irods_zone_name": "<ZONE>",
    "schema_name": "irods_environment",
    "schema_version": "v3"
}

```

# Using davrods under linux

If you want to access data via the commandline interface or python it is handy to install davfs2:

```
sudo apt-get install davfs2
usermod -aG davfs2 username
```

Mount the iRODS filesystem for your user:

```
mount -t davfs https://<IP or FQDN> /mnt/npec/
sudo chown -R christine:christine /mnt/npec/npecZone/home/christine
```

Now you can access data and change data in python:

```
In [1]: import os

In [2]: path = "/mnt/npec/npecZone/home/christine/"

In [3]: os.listdir(path)
Out[3]: 
['Alice-DE.txt',
 'aliceInWonderland',
 'books',
 'Epic-Bugfixes',
 'image.img',
 'image10G.img',
 'image2G.img',
 'image3G.img',
 'image4G.img',
 'image5G.img',
 'test.txt',
 'test1.txt']

In [4]: with open(path+"Alice-DE.txt", "r") as f:
   ...:     content = f.readlines()
   ...:     

In [5]: newContent = ['My line of Alice in wonderland. \n']+content

In [6]: with open(path+"Alice-DE.txt", "w") as f:
   ...:     for item in newContent:
   ...:         f.write(item)
   ...:         

```





