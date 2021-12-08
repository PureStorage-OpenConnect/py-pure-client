# list all nfs export policy rules
res = client.get_nfs_export_policies_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all nfs export policy rules for export_policy 'export_policy_1'
res = client.get_nfs_export_policies_rules(policy_names=['export_policy_1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List nfs export policy rule named 'export_policy_1.1'
res = client.get_nfs_export_policies_rules(names=['export_policy_1.1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token, ids, policy_ids
# See section "Common Fields" for examples
