# list all nfs export policies
res = client.get_nfs_export_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list nfs export policies specified by name
res = client.get_nfs_export_policies(names=['export_policy_1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List nfs export policies specified by id.
res = client.get_nfs_export_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
