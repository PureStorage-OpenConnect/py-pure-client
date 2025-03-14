# delete export by name
res = client.delete_file_system_exports(names=['_array_server::SMB::fs1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete exports by ids
res = client.delete_file_system_exports(ids=['10314f42-020d-7080-8013-000ddt400013'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
