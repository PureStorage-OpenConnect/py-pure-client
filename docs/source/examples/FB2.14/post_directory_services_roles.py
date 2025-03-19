from pypureclient.flashblade.FB_2_14 import DirectoryServiceRole

# create Directory Services role configuration
ARRAY_ADMIN_GRP = 'admins'
GROUP_BASE = 'ou=purestorage,ou=us'
ROLE_NAME = 'array_admin'

directory_service_role = DirectoryServiceRole(role={"name": ROLE_NAME}, group_base=GROUP_BASE, group=ARRAY_ADMIN_GRP)
res = client.post_directory_services_roles(names=['some-role-name'],
                                           directory_service_roles=directory_service_role)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

