# list all targets
res = client.get_targets()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first three targets using default sort
res = client.get_targets(limit=3)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first three targets and sort by address
res = client.get_targets(limit=3, sort='address')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining targets
res = client.get_targets(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter to see only targets that match a specific ip format
res = client.get_targets(filter='name=\'12.56.23.*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset
# See section "Common Fields" for examples
