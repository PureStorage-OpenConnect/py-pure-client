from pypureclient.flashblade import GroupQuota

file_system_name = "quotaFs"

# Add a quota of 1024000 for the file system to apply to the groups with ids 998 and 999
res = client.post_quotas_groups(file_system_names=[file_system_name], gids=[998, 999],
                                quota=GroupQuota(quota=1024000))
# print the created quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Add a quota of 2048000 for the file system to apply to the groups with names group1 and group2
res = client.post_quotas_groups(file_system_names=[file_system_name],
                                group_names=["group1", "group2"],
                                quota=GroupQuota(quota=2048000))
# print the created quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: file_system_ids
# See section "Common Fields" for examples
