# list admin cache entry
res = client.get_admins_cache(names=['adminuser'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# refresh admin cache entry for user with id '10314f42-020d-7080-8013-000ddt400090'
res = client.get_admins_cache(ids=['10314f42-020d-7080-8013-000ddt400090'],
                              refresh=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
