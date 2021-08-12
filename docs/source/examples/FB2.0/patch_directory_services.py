from pypureclient.flashblade import DirectoryService

# update Directory Services smb configuration to specify a join OU in an LDAP server
name = 'smb'
URI = 'ldaps://ad1.mycompany.com'
BASE_DN = 'DC=mycompany,DC=com'
BIND_USER = 'CN=John,OU=Users,DC=mycompany,DC=com'
BIND_PW = 'johnldappassword'

SMB_JOIN_OU = 'OU=PureStorage,OU=StorageArrays,OU=ServiceMachines'
SMB_ATTRS = {'join_ou': SMB_JOIN_OU}

directory_service = DirectoryService(base_dn=BASE_DN, bind_password=BIND_PW, bind_user=BIND_USER, uris=[URI],
                                     enabled=True, smb=SMB_ATTRS)
res = client.patch_directory_services(names=[name], directory_service=directory_service)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update Directory Services nfs configuration to use an NIS configuration
name = 'nfs'
MASTER_SERVER_HOSTNAME = 'nis.master.server.example.com'
BACKUP_SERVER_HOSTNAME = 'nis.backup.server.example.com'
BACKUP_SERVER_IP = '188.123.4.43'
nis_servers = [MASTER_SERVER_HOSTNAME, BACKUP_SERVER_IP, BACKUP_SERVER_HOSTNAME]

NIS_DOMAIN = 'my-nis-domain'
NFS_ATTRS = {'nis_domains': [NIS_DOMAIN], 'nis_servers': nis_servers}

# the only fields needed in order to enable the nfs directory service when configuring
# NIS are an NIS domain and NIS servers
directory_service = DirectoryService(enabled=True, nfs=NFS_ATTRS)
res = client.patch_directory_services(names=[name],
                                      directory_service=directory_service)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update the management directory service to use an Oracle Unified Directory server,
# specifying our user object class as "inetOrgPerson" and our login attribute as
# "givenName"
name = 'management'
OUD_URI = 'ldap://my-oud-leader.example.com'
OUD_BASE_DN = 'DC=example,DC=com'
OUD_BIND_USER = 'CN=ServiceAcct,OU=Users,DC=example,DC=com'
OUD_BIND_PW = 'something-absurdly-complex'

USER_LOGIN_ATTR = 'givenName'
USER_OBJ_CLASS = 'inetOrgPerson'
MGMT_ATTRS = {'user_login_attribute': USER_LOGIN_ATTR,
              'user_object_class': USER_OBJ_CLASS}
directory_service = DirectoryService(base_dn=OUD_BASE_DN, bind_password=OUD_BIND_PW,
                                     bind_user=OUD_BIND_USER, uris=[OUD_URI],
                                     enabled=True, management=MGMT_ATTRS)
res = client.patch_directory_services(names=[name],
                                      directory_service=directory_service)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
