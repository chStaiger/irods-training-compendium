# Installing YODA test server

## Prerequisites
### YODA server preparations
- Centos machine (centos 7.9)
- You need a login account with sudo rights (without password confirmation) to later run the ansible scripts from your local machine. Create `/etc/sudoers.d/username` with `username ALL=(ALL) NOPASSWD:ALL`
- Info: It is not enough to simply add the account to group "wheel" and using `-K` for `ansible-playbook`. It fails to install `moai` correctly (because the home directory of the loginaccount is used instead of the `moai` homedir).
- add your SSH public key to `.ssh/authorized_keys`
- yum update to get the latest certificates.
  Otherwise, the ansible task `Import RPM key for NodeSource` will fail.

- Add the following as the first line of /etc/hosts:

  `127.0.0.1 combined.yoda.test combined`

  The address must be 127.0.0.1, so that a self-signed certificate can be used during the installation.  A bug in iRODS causes the server to connect to itself for some tasks (for example, to install schemas in`/tempZone/yoda/schemas`), so the certificate is used and will fail validation if the "remote" ICAT server is not 127.0.0.1.

## Local machine preparations
The YODA installation works with ansible scripts. On you local machine we will install ansible and you will issue the commands to install YODA on the prepared YODA server from your local machine.

- On your local machine install ansible, version >= 2.9
- Clone the YODA ansible scripts from github:
```
  git clone https://github.com/UtrechtUniversity/yoda.git
  cd yoda
```

## Ansible configuration
In the ansible folder you will find several configuration files for ansible to execute the installation process. We need to adjust then such that ansible knows which server to install.
 - In `environments/development/allinone/host_vars/combined`, change
   the address of ansible_host to the IP name or IP address of the remote host

 - In `environments/development/allinone/group_vars/allinone.yml`,
   change `ansible_user` to the login account on the YODA server, and change
   `ansible_ssh_private_key_file` to the full path of your local private key for that user (see section 1).

## Install YODA
 - On your local machine run:
 ```
   ansible-playbook -i environments/development/allinone playbook.yml
 ```

## Accessing YODA
To access the YODA frontend through the web browser on your local machine you will need to set the mapping between fully qualified host name or IP address of the YODA server and the respective webpages on the YODA server.
Add to your /etc/hosts file on your local machine:
```
<fqdn or IP> api.eus.yoda.test
<fqdn or IP> portal.yoda.test
<fqdn or IP> data.yoda.test
<fqdn or IP> public.data.yoda.test
<fqdn or IP> public.yoda.test
```

Don't forget to allow port 80 and 443 on the linux machine.

To get to the YODA interface simply type into your browser `portal.yoda.test`

## Testdata
You can populate your YODA instance with some testdata by running

```
ansible-playbook -i environments/development/allinone test.yml
```

This will install the following YODA and iRODS users:

```
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'researcher'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'viewer'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'groupmanager'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'datamanager'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'functionaladmingroup'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'functionaladmincategory'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'functionaladminpriv'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsadmin', u'name': u'technicaladmin'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'projectmanager'})
changed: [combined] => (item={u'password': u'test', u'type': u'rodsuser', u'name': u'dmcmember'})
```

