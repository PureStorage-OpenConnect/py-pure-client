# list all replica links
res = client.get_file_system_replica_links()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list first five replica links and sort by local file system
res = client.get_file_system_replica_links(limit=5, sort='local_file_system.name')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list remaining replica links
res = client.get_file_system_replica_links(continuation_token = res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list replica links on the remote
res = client.get_file_system_replica_links(remote_names=['myremote'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with filter to see only replica links that are paused
res = client.get_file_system_replica_links(filter='paused')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, local_file_system_ids, local_file_system_names, offset,
#                     remote_file_system_ids, remote_file_system_names, remote_ids
# See section "Common Fields" for examples
