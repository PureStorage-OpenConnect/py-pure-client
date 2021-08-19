res = client.get_arrays_supported_time_zones()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, names, offset, sort
# See section "Common Fields" for examples
