# List all user quotas for the file system
res = client.get_quotas_users(file_system_names=["quotaFs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, file_system_ids, filter, limit, names, offset, sort,
#                     uids, user_names
# See section "Common Fields" for examples
