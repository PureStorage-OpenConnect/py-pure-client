# list all network interfaces
res = client.get_network_interfaces()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_network_interfaces(limit=5, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_network_interfaces(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining network interfaces
res = client.get_network_interfaces(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_network_interfaces(filter='(services=\'replication\')')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset
# See section "Common Fields" for examples
