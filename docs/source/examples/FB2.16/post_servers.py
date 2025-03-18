from pypureclient.flashblade import ServerPost

# post the server object myserver on the array
# Please note: create_ds parameter is required and it is value should be <server-name>_nfs
attr = ServerPost()
res = client.post_servers(names=["myserver"], server=attr, create_ds="myserver_nfs")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
