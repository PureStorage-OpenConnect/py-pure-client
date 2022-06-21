# list all drives
res = client.get_drives()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of drives by name
res = client.get_drives(names=['CH1.FB1.BAY3', 'CH1.FB2.BAY1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of drives by id
res = client.get_drives(ids=['f9330b89-fb7c-cc8a-07b7-bfb086873982',
                             'a1f9faf6-18b5-7c9d-d816-6df3d2db6dca'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all healthy drives
res = client.get_drives(filter='status=\'healthy\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, limit, offset, sort, total_only
# See section "Common Fields" for examples
