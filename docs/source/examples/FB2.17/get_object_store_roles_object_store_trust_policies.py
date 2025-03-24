# list trust policy by object store role id
res = client.get_object_store_roles_object_store_trust_policies(role_ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list trust policy by object store role name
res = client.get_object_store_roles_object_store_trust_policies(role_names=["acc1/myobjrole"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list trust policy by trust policy name
res = client.get_object_store_roles_object_store_trust_policies(names=["acc1/myobjrole/trust-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
