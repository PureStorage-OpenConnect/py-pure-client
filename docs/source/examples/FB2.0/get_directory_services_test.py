# test the nfs directory service configuration that exists already
res = client.get_directory_services_test(names=['nfs'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, ids, limit, sort
# See section "Common Fields" for examples
