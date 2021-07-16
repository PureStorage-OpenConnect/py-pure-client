# post the object store user object myobjuser on the array without full access
res = client.post_object_store_users(names=["acc1/myobjuser"], full_access=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
