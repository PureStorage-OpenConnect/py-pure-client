# list all admin accounts (given sufficient permissions)
res = client.get_admins()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of admin accounts by name with api token exposed
res = client.get_admins(names=['pureuser'], expose_api_token=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of admin accounts by id
res = client.get_admins(ids=['10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
