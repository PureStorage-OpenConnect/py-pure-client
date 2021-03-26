# list all roles
res = client.get_roles()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list role for readonly user
res = client.get_roles(names=["readonly"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, ids, filter, limit, offset, sort
# See section "Common Fields" for examples
