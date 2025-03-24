# list all object store virtual hosts
res = client.get_object_store_virtual_hosts()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by created in descendant order
res = client.get_object_store_virtual_hosts(limit=3, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 3
res = client.get_object_store_virtual_hosts(limit=3)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_object_store_virtual_hosts(filter='name=\'s3.myhost*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list by name
res = client.get_object_store_virtual_hosts(names=['s3.myhost*'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list by id
res = client.get_object_store_virtual_hosts(ids=['10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, offset
# See section "Common Fields" for examples
