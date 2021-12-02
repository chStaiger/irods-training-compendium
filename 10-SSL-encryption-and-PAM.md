# Encrypting iRODS with SSL and allowing authentication through PAM

This document describes how to setup security on the iRODS server and allow users 
to authenticate via LDAP. The settings in this document are tailored towards iRODS instances running on linux servers hosted by FBIT at WUR. I.e. we make use of the linux servers connection to the active directory and enable users known in WUR's active directory.

## Environment
The documentation is tested with an Ubuntu 18.04 server.
The ducmentation is leveraging on 
https://github.com/sara-nl/iRODS-UIs-APIs/blob/master/Davrods_install_guide.md
https://docs.irods.org/4.2.7/plugins/pluggable_authentication/#pam-pluggable-authentication-module

## SSL encryption
To setup secure connection between clients and the iRODS server we set up SSL encryption on the iRODS server. 

**Please note:** If your iRODS server is part of a federation and you are using SSL encryption *all other* iRODS servers have  to be enabled with SSL encryption, too.

### Generate certificates

1. **Generate the SSL key and certificate** on the server that runs iRODS
 ```sh
 sudo su - irods
 mkdir /etc/irods/ssl
 cd /etc/irods/ssl
 openssl genrsa -out irods.key 2048
 chmod 600 irods.key
 openssl req -new -x509 -key irods.key -out irods.crt -days 3650
 ```

 You are asked to provide some details.

 ```sh
Country Name (2 letter code) [XX]:XX
State or Province Name (full name) []:<your state>
Locality Name (eg, city) [Default City]:<your city>
Organization Name (eg, company) [Default Company Ltd]:<company>
Organizational Unit Name (eg, section) []:<group>
Common Name (eg, your name or your server's hostname) []:<ip address or fqdn>
Email Address []:<email>
 ```
The common name that you set here will also be used by all user clients and Davrods to address the iRODS server. It should  correspond to the fqdn or the hostname you set in the */etc/hosts* file.
You might also have to adjust the */etc/irods/hosts_config.json* to match the fqdn in the certificate.

 ```sh
 openssl dhparam -2 -out dhparams.pem 2048
 ```
2. **Adjust the /etc/irods/core.re** with

 ```sh
 acPreConnect(*OUT) { *OUT="CS_NEG_REQUIRE"; }
 ```
3. **Adjust the environment-json for the irods service account.**

   You need to set the server certificate (*irods.crt*) and its corresponding key (*irods.key*) and the certfificate from the "Certificate Authority" (here we use again *irods.crt* (usually you would have a *chain.pem*), if you use a different authority make sure all machines that run clients have this file installed). We also need to set the file defining how keys are exchanged (*dhparams.pem*). Finally we need to tell iRODS that we are using ssll verification by certificate. 

   The irods environment file for the unix service account can be in several locations, please check what is applicable to you:

 ```sh
 vi /var/lib/irods/.irods/irods_environment.json # default
 vi /home/irods/.irods/irods_environment.json # if irods service account has a home
 ```

 ``` sh
 "irods_client_server_policy": "CS_NEG_REQUIRE",
 "irods_ssl_certificate_chain_file": "/etc/irods/ssl/irods.crt",
 "irods_ssl_certificate_key_file": "/etc/irods/ssl/irods.key",
 "irods_ssl_dh_params_file": "/etc/irods/ssl/dhparams.pem",
 "irods_ssl_ca_certificate_file": "/etc/irods/ssl/irods.crt",
 "irods_ssl_verify_server": "cert"
 ```
 Make sure common name of the server in the certificate and the *irods_host* in the environment json file match.
 Then try as the user 'irods' whether you can login:

 ```sh
 iinit
 ils
 ```
4. **Enabling other user clients with SSL.**

   Clients on other servers need to have a copy of the chain of trust pem-file (here the *irods.crt*) file.
    All your iRODS users need to extend their *irods_environment.json* with

 ```sh
 "irods_client_server_negotiation": "request_server_negotiation",
 "irods_client_server_policy": "CS_NEG_REQUIRE",
 "irods_ssl_ca_certificate_file": "</path/to>/irods.crt",
 "irods_encryption_key_size": 32,
 "irods_encryption_salt_size": 8,
 "irods_encryption_num_hash_rounds": 16,
 "irods_encryption_algorithm": "AES-256-CBC"
 ```

## Enabling authentication through PAM
Prerequisite for enabling PAM-authentication is that iRODS itself makes use of SSL encryption. SSL encryption is used to communicate safely with the LDAP.
If the iRODS client specifies that authentication should take place through PAM, the iRODS server will look for the specifications in */etc/pam.d/irods* to try to authenticate the user. 

1. Testing if iRODS uses the PAM module
 For testing purposes we will allow all users to authenticate with any password:
 ```sh
 sudo su - root -c 'echo "auth sufficient pam_permit.so" > /etc/pam.d/irods'
 ```

​      And check with
 ```
 /usr/sbin/irodsPamAuthCheck bob
 <some password string>
 Authenticated
 ```
​     whether iRODS uses the pam module.

2. For common linux servers the following chain in the iRODS PAM module is sufficient:
 ```sh
 cat /etc/pam.d/irods
 auth        required      pam_env.so
 auth        sufficient    pam_unix.so
 auth        requisite     pam_succeed_if.so uid >= 500 quiet
 auth        required      pam_deny.so
 ```

3. Linux servers hosted by FBIT should use for iRODS the same authentication chain as in */etc/pam.d/common-auth*

 ```sh
 cat /etc/pam.d/irods

 #auth sufficient pam_permit.so

 auth    [success=3 default=ignore]      pam_krb5.so minimum_uid=1000
 auth    [success=2 default=ignore]      pam_unix.so nullok_secure try_first_pass
 auth    [success=1 default=ignore]      pam_sss.so use_first_pass
 # here's the fallback if no module succeeds
 auth    requisite                       pam_deny.so
 # prime the stack with a positive return value if there isn't one already;
 # this avoids us returning an error just because nothing sets a success code
 # since the modules above will each just jump around
 auth    required                        pam_permit.so
 # and here are more per-package modules (the "Additional" block)
 auth    optional                        pam_cap.so

 ```

4. Adjust the user icommands environment file
 Users will need to have a local copy of the certificate file *irods.crt*.
 ```
 cat .irods/irods_environment.json
 {
     "irods_host": "<IP or FQDN>",
     "irods_port": 1247,
     "irods_zone_name": "elabZone",
     "irods_user_name": "<LDAP username>",
     "irods_client_server_negotiation": "request_server_negotiation",
     "irods_client_server_policy": "CS_NEG_REQUIRE",
     "irods_encryption_key_size": 32,
     "irods_encryption_salt_size": 8,
     "irods_encryption_num_hash_rounds": 16,
     "irods_encryption_algorithm": "AES-256-CBC",
     "irods_ssl_ca_certificate_file": "/home/<path to>/irods.crt",
     "irods_authentication_scheme": "PAM"
 }
 ```
