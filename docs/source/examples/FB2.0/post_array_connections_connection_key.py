# post to the array-connections/connection-key endpoint to get a connection key
res = client.post_array_connections_connection_key()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
