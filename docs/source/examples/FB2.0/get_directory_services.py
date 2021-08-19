# list Directory Services configuration
res = client.get_directory_services(names=["nfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
