res = client.get_support()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: ids, names
# See section "Common Fields" for examples
