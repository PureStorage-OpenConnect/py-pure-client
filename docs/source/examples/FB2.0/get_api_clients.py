# List all configured api clients.
res = client.get_api_clients()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List first two api clients beginning with 'my_oauth'. Use default sorting.
res = client.get_api_clients(limit=2, names=["my_oauth"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List the first api client when sorting by name.
res = client.get_api_clients(limit=1, sort="name")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List an api client by id.
res = client.get_api_clients(ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List all api_clients servers that are enabled.
res = client.get_api_clients(filter='enabled=\"True\"')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, offset
# See section "Common Fields" for examples
