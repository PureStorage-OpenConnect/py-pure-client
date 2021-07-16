# post the object store account object myobjaccount on the array
res = client.post_object_store_accounts(names=["myobjaccount"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
