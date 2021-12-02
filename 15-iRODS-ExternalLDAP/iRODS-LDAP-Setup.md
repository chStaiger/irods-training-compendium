# How-to: Connecting iRODS and external LDAP

## Prerequisites

- iRODS instance enabled with SSL
- LDAP server, SSL certified

## Install procedure

1. Install libpam-ldap

   - **ldap**://\<fqdn\> or **ldaps**://\<fqdn\>
   - Distinguished name: dc=\<name\>,dc=nl

   - LDAP version 3

   - Make local root Database admin: yes

   - Does LDAP database require login: No

   - LDAP account for root: cn=admin,dc=m-unlock,dc=nl

   - LDAP root password: looooooooongpassword

2. sudo pam-auth-update: unstar LDAP box

3. /etc/pam.d/irods --> auth sufficient pam_ldap.so

4. If you use **ldaps** you need to adjust the settings in `/etc/ldap.conf

   1. ssl on
   2. tls_checkpeer yes
   3. tls_cacertfile /etc/ssl/\<your-ca\>.cert

5. Environment json for ldap users:

   ```
   {
       "irods_host": "<fqdn>",
       "irods_port": 1247,
       "irods_zone_name": "<zone>",
       "irods_user_name": "<user name from ldap>", 
       "irods_client_server_negotiation": "request_server_negotiation",
       "irods_client_server_policy": "CS_NEG_REQUIRE",
       "irods_encryption_key_size": 32,
       "irods_encryption_salt_size": 8,
       "irods_encryption_num_hash_rounds": 16,
       "irods_encryption_algorithm": "AES-256-CBC",
       "irods_ssl_ca_certificate_file": "irods.crt",
       "irods_authentication_scheme": "PAM"
   }
   ```
  

