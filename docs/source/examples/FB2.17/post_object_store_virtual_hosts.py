# post the object store virtual host on the array
res = client.post_object_store_virtual_hosts(names=["s3.myhost.com"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
