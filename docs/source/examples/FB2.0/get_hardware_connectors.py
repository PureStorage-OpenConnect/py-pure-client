# list all hardware connectors
res = client.get_hardware_connectors()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_hardware_connectors(limit=5, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_hardware_connectors(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining hardware connectors
res = client.get_hardware_connectors(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_hardware_connectors(filter='port_count=4')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: offset, ids, names
# See section "Common Fields" for examples
