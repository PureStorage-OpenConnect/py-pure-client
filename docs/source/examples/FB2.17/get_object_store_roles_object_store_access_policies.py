# list access policies for object store roles
res = client.get_object_store_roles_object_store_access_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific role
res = client.get_object_store_roles_object_store_access_policies(member_names=["acc1/myobjrole"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific role by id
res = client.get_object_store_roles_object_store_access_policies(member_ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only roles with full access
res = client.get_object_store_roles_object_store_access_policies(policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only roles with a specific policy by id
res = client.get_object_store_roles_object_store_access_policies(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
