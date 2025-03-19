# get all file system exports
res = client.get_file_system_exports()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get exports by name
res = client.get_file_system_exports(names=['_array_server::SMB::fs1',
                                            '_array_server::NFS::fs1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get exports by ids
res = client.get_file_system_exports(ids=['10314f42-020d-7080-8013-000ddt400013',
                                          '10314f42-020d-7080-8013-000ddt400014'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
