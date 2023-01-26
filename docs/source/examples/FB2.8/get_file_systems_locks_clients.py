# Get all the clients (limit the result to 1000) who have acquired file locks
res = client.get_file_systems_locks_clients(limit=1000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, continuation_token
# See section "Common Fields" for examples