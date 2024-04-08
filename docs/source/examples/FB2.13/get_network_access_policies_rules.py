# list all network access policy rules
res = client.get_network_access_policies_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all network access policy rules for policy 'default-network-rules'
res = client.get_network_access_policies_rules(policy_names=['default-network-access-policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List network access policy rule named 'default-network-rules.1' for policy 'default-network-rules'
res = client.get_network_access_policies_rules(names=['default-network-access-policy.1'],
                                               policy_names=['default-network-access-policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token, ids, policy_ids
# See section "Common Fields" for examples
