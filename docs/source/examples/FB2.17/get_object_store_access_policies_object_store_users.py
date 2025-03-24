# list access policies for object store users
res = client.get_object_store_access_policies_object_store_users()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific user
res = client.get_object_store_access_policies_object_store_users(member_names=["acc1/myobjuser"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list access policies for specific user by id
res = client.get_object_store_access_policies_object_store_users(member_ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only users with full access
res = client.get_object_store_access_policies_object_store_users(policy_names=["pure:policy/full-access"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only users with a specific policy by id
res = client.get_object_store_access_policies_object_store_users(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
