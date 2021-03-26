res = client.get_arrays_eula()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
