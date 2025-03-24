from pypureclient.flashblade.FB_2_17 import ObjectStoreRole

# update role by role name
res = client.patch_object_store_roles(names=["acc1/myobjrole"],
                                      object_store_role=ObjectStoreRole(max_session_duration=7200))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# update role by role id
res = client.patch_object_store_roles(ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"],
                                      object_store_role=ObjectStoreRole(max_session_duration=7200))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
