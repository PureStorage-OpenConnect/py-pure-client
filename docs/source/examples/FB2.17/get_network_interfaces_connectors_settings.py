# list all global network settings for network connectors
res = client.get_network_interfaces_connectors_settings()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_network_interfaces_connectors_settings(limit=5, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_network_interfaces_connectors_settings(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: offset, ids, names, continuation_token, filter
# See section "Common Fields" for examples
