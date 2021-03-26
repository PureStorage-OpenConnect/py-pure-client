from pypureclient.flashblade import GroupQuota

file_system_name = "quotaFs"

# Update the quota for the groups with with ids 998 and 999 to be 2048000
res = client.patch_quotas_groups(file_system_names=[file_system_name],
                                 gids=[998, 999],
                                 quota=GroupQuota(quota=2048000))
# print the created quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the quota for the groups with names group1 and group2 to be 1024000
res = client.patch_quotas_groups(file_system_names=[file_system_name],
                                 group_names=["group1", "group2"],
                                 quota=GroupQuota(quota=1024000))
# print the updated quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: file_system_ids, names
# See section "Common Fields" for examples
