# Workflow: Archiving research data

**Author: **Christine Staiger (WUR)

## Synopsis

Assume researchers have access to an own iRODS instance which implements their data policies and contains all data they need during the active research phase. How can researchers then bring data in archived state in a YODA instance?

Here we show the setup between an iRODS server and a YODA instance; furthermore we give an example workflow how dtaa can be manually transferred from iRODS to the respective research group in YODA.



## Prerequisites

- Test YODA instance as described in *Install-Yoda.md*.
- Test iRODS instance
- Federation between the iRODS instance and YODA instance as described in *Federate-Yoda.md*

## Technical Setup

1. Once you have populated the YODA instance with the test data, there will be a user `researcher` on your YODA instance.

2. Create a user on the iRODS instance and add it as a remote user on the YODA instance:

   ```
   -bash-4.2$ iadmin lu
   rods#tempZone
   anonymous#tempZone
   yodaresearcher@gmail.com#tempZone
   yodadatamanager@gmail.com#tempZone
   researcher#tempZone
   viewer#tempZone
   groupmanager#tempZone
   datamanager#tempZone
   functionaladmingroup#tempZone
   functionaladmincategory#tempZone
   functionaladminpriv#tempZone
   technicaladmin#tempZone
   projectmanager#tempZone
   dmcmember#tempZone
   christine#irodsZone
   ```

   For sake of argument assume that `researcher#tempZone`is the YODA account and `christine#irodsZone`is the respective user on th iRODS instance. Both accounts belong to the same person.

3. Now we need to add the federated iRODS account `christine#irodsZone` to the respective YODA groups where  `researcher#tempZone`is a member of. E.g.

   ```
   -bash-4.2$ iadmin lg research-initial
   Members of group research-initial:
   groupmanager#tempZone
   rods#tempZone
   researcher#tempZone
   functionaladminpriv#tempZone
   ```

   And add the remote account to the group

   ```
   -bash-4.2$ iadmin atg research-initial christine#irodsZone
   -bash-4.2$ iadmin lg research-initial
   Members of group research-initial:
   groupmanager#tempZone
   rods#tempZone
   researcher#tempZone
   functionaladminpriv#tempZone
   christine#irodsZone
   
   ```

4. On the iRODS instance the user `christine` can now list the respective remote folder in the YODA instance

   ```
   ubuntuadmin@euw-vm-irods-test:~$ ils /tempZone/home/research-initial/testdata
   /tempZone/home/research-initial/testdata:
     lorem.txt
     SIPI_Jelly_Beans_4.1.07.tiff
   ```

5. Search for data in the remote zone of YODA:

   ```
   iquest -z tempZone "SELECT COLL_NAME, DATA_NAME"
   ```

6. Data between the two iRODS instances can be exchenged with

   ```
   irsync i:/irodsZone/home/christine/helloFromIrods.txt i:/tempZone/home/research-initial/helloFromIrods.txt
   ```

   

