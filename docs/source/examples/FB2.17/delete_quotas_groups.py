# Assume you have a file system named quotaFs
file_system_name = "quotaFs"

# Delete the quotas of groups on the file system with ids 998 and 999
client.delete_quotas_groups(file_system_names=[file_system_name], gids=[998, 999])

# Delete the quotas of groups on the file system with names group1 and group2
client.delete_quotas_groups(file_system_names=[file_system_name],
                            group_names=["group1", "group2"])

# Other valid fields: context_names, file_system_ids, names
# See section "Common Fields" for examples
