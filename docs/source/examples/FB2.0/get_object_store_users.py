# list all object store users
res = client.get_object_store_users()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by created in descendant order
res = client.get_object_store_users(limit=5, sort="created-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_object_store_users(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining object store users
res = client.get_object_store_users(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_object_store_users(filter='name=\'acc1/myobjuser*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset
# See section "Common Fields" for examples
