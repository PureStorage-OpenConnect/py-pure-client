# Get all file locks and limit the number of returned entries to 1000
res = client.get_file_systems_locks(limit=1000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get a single lock information by lock name
res = client.get_file_systems_locks(names="3-NFSv3-0-1024")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all locks created by a client with specified client IP
res = client.get_file_systems_locks(client_names='1.1.1.1')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get locks for a specific file
res = client.get_file_systems_locks(file_system_names='root', paths='/dir/file')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))


# Other valid fields: file_system_ids, filter, inodes, continuation_token
# See section "Common Fields" for examples