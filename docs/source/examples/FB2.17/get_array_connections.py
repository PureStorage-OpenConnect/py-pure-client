# list all array connections
res = client.get_array_connections()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all array connections with remote name "otherarray"
res = client.get_array_connections(remote_names=["otherarray"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all array connections with remote id '10314f42-020d-7080-8013-000ddt400090'
res = client.get_array_connections(remote_ids=['10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list first five array connections and sort by source in descendant order
res = client.get_array_connections(limit=5, sort="version-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining array connections
res = client.get_array_connections(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with filter to see only array connections on a specified version
res = client.get_array_connections(filter='version=\'3.*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, offset
# See section "Common Fields" for examples
