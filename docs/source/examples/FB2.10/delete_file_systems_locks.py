# Delete all locks created by a specified client IP
res = client.delete_file_systems_locks(client_names='1.1.1.1')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete a single lock by name
res = client.delete_file_systems_locks(names='3-NFSv3-0-1024')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all locks for a specific file
res = client.delete_file_systems_locks(file_system_names='root', paths='/dir/file')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all locks for files (recursively) within a specified folder
res = client.delete_file_systems_locks(file_system_names='root', paths='/dir',
                                       recursive=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: file_system_ids, inodes, references
# See section "Common Fields" for examples