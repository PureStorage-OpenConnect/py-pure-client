# list all array connection paths
res = client.get_array_connections_path()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list first five array connection paths using default sort
res = client.get_array_connections_path(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list first five array connection paths and sort by source in descendant order
res = client.get_array_connections_path(limit=5, sort="source-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining array connection paths
res = client.get_array_connections_path(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with filter to see only array connection paths from a specified source ip
res = client.get_array_connections_path(filter='source=\'10.202.101.70\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, remote_ids, remote_names, offset
# See section "Common Fields" for examples
