# Advanced rules

### Become a user as admin

```
sudo su - irods
export clientUserName=<user>
# all commands and rules will be executed as the user
export clientUserName=<rodsadmin>
```

Get all users:

```
iquest "SELECT USER_NAME where USER_TYPE like 'rodsadmin' || like'rodsuser'"
```



