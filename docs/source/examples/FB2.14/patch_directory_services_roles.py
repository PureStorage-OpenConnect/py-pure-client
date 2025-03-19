from pypureclient.flashblade.FB_2_14 import DirectoryServiceRole, ReferenceWritable

# update Directory Services role configuration
ARRAY_ADMIN_GRP = 'admins'
GROUP_BASE = 'ou=purestorage,ou=us'
CONFIG_NAME = 'example-role-mapping'

NEW_ROLE_NAME = 'array_admin'
role_reference = ReferenceWritable(name=NEW_ROLE_NAME)

directory_service_role = DirectoryServiceRole(group_base=GROUP_BASE, group=ARRAY_ADMIN_GRP, role=role_reference)
res = client.patch_directory_services_roles(names=[CONFIG_NAME],
                                            directory_service_roles=directory_service_role)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: role_ids, ids, role_names
# See section "Common Fields" for examples
