# list all smb share policy rules
res = client.get_smb_share_policies_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all smb share policy rules for share_policy 'share_policy_1'
res = client.get_smb_share_policies_rules(policy_names=['share_policy_1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List smb share policy rule named 'everyone' for policy 'share_policy_1'
res = client.get_smb_share_policies_rules(policy_names=['share_policy_1'],
                                          names=['everyone'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort,
#                     continuation_token, ids, policy_ids
# See section "Common Fields" for examples
