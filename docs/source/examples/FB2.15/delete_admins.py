# Delete the admins by names.
res = client.delete_admins(names=['test-admin'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete the admins with id '10314f42-020d-7080-8013-000ddt400090'
res = client.delete_admins(ids=['10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

