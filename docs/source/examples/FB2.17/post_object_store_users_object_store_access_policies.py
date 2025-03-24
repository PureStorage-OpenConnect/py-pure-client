# add a policy to a user
res = client.post_object_store_users_object_store_access_policies(
    member_names=["acc1/myobjuser"], policy_names=["pure:policy/bucket-list"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# add a member to a policy by id
res = client.post_object_store_users_object_store_access_policies(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
