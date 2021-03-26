# Test active directory accounts
res = client.get_active_directory_test()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, ids, limit, names, sort
# See section "Common Fields" for examples
