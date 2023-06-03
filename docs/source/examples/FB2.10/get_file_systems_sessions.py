# List all sessions, limit response to 10
res = client.get_file_systems_sessions(limit=10)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get single session by name
res = client.get_file_systems_sessions(names='54043195528445954')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all sessions created by a client with specified client IP
res = client.get_file_systems_sessions(client_names='1.1.1.1')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all sessions with specified protocol
res = client.get_file_systems_sessions(protocols='nfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all sessions created by a client with specified user
res = client.get_file_systems_sessions(user_names='0:0')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token
# See section "Common Fields" for examples

