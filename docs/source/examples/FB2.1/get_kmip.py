# List the KMIP server configurations
res = client.get_kmip()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: names, ids, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
