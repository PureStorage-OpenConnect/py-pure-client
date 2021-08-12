# list all object store accounts
res = client.get_object_store_accounts()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by unique in descendant order
res = client.get_object_store_accounts(limit=5, sort="space.unique-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_object_store_accounts(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining object store accounts
res = client.get_object_store_accounts(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_object_store_accounts(filter='name=\'myobjaccount*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset, total_only
# See section "Common Fields" for examples
