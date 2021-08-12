# List the array's factory reset token
res = client.get_arrays_factory_reset_token()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
