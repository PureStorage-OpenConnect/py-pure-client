# list all rules of a specific object store access policy by role name
res = client.get_object_store_roles_object_store_trust_policies_rules(role_names=["acc1/myobjrole"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all rules of a specific object store access policy by role id
res = client.get_object_store_roles_object_store_trust_policies_rules(role_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list rules for specific policy
res = client.get_object_store_roles_object_store_trust_policies_rules(policy_names=["acc1/myobjrole/trust-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list specific rule name
res = client.get_object_store_roles_object_store_trust_policies_rules(policy_names=["acc1/myobjrole/trust-policy"], names=["myrule"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list specific rule index
res = client.get_object_store_roles_object_store_trust_policies_rules(policy_names=["acc1/myobjrole/trust-policy"], indices=[1])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
