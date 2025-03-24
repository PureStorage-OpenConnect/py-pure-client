# list all object store roles
res = client.get_object_store_roles()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by created in descendant order
res = client.get_object_store_roles(limit=5, sort="created-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_object_store_roles(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining object store roles
res = client.get_object_store_roles(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_object_store_roles(filter='name=\'acc1/myobjrole*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, names, offset
# See section "Common Fields" for examples
