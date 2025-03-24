# list all smb client policy rules
res = client.get_smb_client_policies_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all smb client policy rules for client policy 'client_policy_1'
res = client.get_smb_client_policies_rules(policy_names=['client_policy_1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List smb client policy rule named 'client_policy_1.1' for policy 'client_policy_1'
res = client.get_smb_client_policies_rules(policy_names=['client_policy_1'],
                                          names=['client_policy_1.1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort, continuation_token, ids, policy_ids
# See section "Common Fields" for examples