# list access policies for object store roles
res = client.get_object_store_access_policies_object_store_roles()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific role
res = client.get_object_store_access_policies_object_store_roles(member_names=["acc1/myobjrole"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific role by id
res = client.get_object_store_access_policies_object_store_roles(member_ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only roles with full access
res = client.get_object_store_access_policies_object_store_roles(policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only roles with a specific policy by id
res = client.get_object_store_access_policies_object_store_roles(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list by (role_name, policy_name), (role_id, policy_id), (role_name, policy_id), and (role_id, policy_name)
res = client.get_object_store_access_policies_object_store_roles(member_names=["acc1/myobjrole"], policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
res = client.get_object_store_access_policies_object_store_roles(member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
res = client.get_object_store_access_policies_object_store_roles(member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
res = client.get_object_store_access_policies_object_store_roles(member_names=["acc1/myobjrole"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
