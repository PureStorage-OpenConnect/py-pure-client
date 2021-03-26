from pypureclient.flashblade import DirectoryServiceRole

# update Directory Services role configuration
ARRAY_ADMIN_GRP = 'admins'
GROUP_BASE = 'ou=purestorage,ou=us'
ROLE_NAME = 'array_admin'

directory_service_role = DirectoryServiceRole(group_base=GROUP_BASE, group=ARRAY_ADMIN_GRP)
res = client.patch_directory_services_roles(role_names=[ROLE_NAME],
                                            directory_service_roles=directory_service_role)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: role_ids, ids
# See section "Common Fields" for examples
