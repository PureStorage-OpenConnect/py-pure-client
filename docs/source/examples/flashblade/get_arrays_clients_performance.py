# list client performance for all clients
res = client.get_arrays_clients_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list client performance for one specific array client
res = client.get_arrays_clients_performance(names=['123.123.123.123:8080'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, sort, total_only
# See section "Common Fields" for examples
