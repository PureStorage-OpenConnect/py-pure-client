# List all group quotas for the file system
res = client.get_quotas_groups(file_system_names=["quotaFs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, offset
# See section "Common Fields" for examples
