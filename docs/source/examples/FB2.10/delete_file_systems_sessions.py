# Delete session by name
res = client.delete_file_systems_sessions(names='54043195528445954')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all sessions of specified protocol
res = client.delete_file_systems_sessions(protocols='nfs', disruptive=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all sessions created by specified user
res = client.delete_file_systems_sessions(user_names='0:0', disruptive=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all sessions created by specified client IP
res = client.delete_file_systems_sessions(client_names='1.1.1.1', disruptive=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete all sessions of specified protocol created by specified client IP and user 
res = client.delete_file_systems_sessions(protocols='nfs',
                                          client_names='1.1.1.1',
                                          user_names='0:0')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

