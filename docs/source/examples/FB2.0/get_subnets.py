# list all subnets
res = client.get_subnets()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_subnets(limit=5, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_subnets(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining subnets
res = client.get_subnets(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_subnets(filter='(services=\'replication\')')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset
# See section "Common Fields" for examples
