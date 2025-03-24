from pypureclient.flashblade.FB_2_17 import ObjectStoreRole

res = client.post_object_store_roles(names=["acc1/myobjrole"], object_store_role=ObjectStoreRole(max_session_duration=7200))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
