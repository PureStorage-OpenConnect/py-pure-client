# Test the KMIP server configuration named "my_kmip_server"
res = client.get_kmip_test(names=["my_kmip_server"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
