# List all group quotas for the file system
res = client.get_quotas_groups(file_system_names=["quotaFs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, file_system_ids, filter, gids, group_names, 
#                     limit, names, offset, sort
# See section "Common Fields" for examples
