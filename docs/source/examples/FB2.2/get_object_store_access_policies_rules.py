# list all object store access policy rules
res = client.get_object_store_access_policies_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list rules for specific policy
res = client.get_object_store_access_policies_rules(policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list rules for specific policy by id
res = client.get_object_store_access_policies_rules(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list specific rule
res = client.get_object_store_access_policies_rules(policy_names=["pure:policy/full-access"], names=["myrule"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
