# Create a factory reset token for the array
res = client.post_arrays_factory_reset_token()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
