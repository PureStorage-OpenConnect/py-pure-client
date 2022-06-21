# list all fans
res = client.get_hardware(filter='type=\'fan\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all XFMs
res = client.get_hardware(filter='type=\'xfm\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all Drives
res = client.get_hardware(filter='type=\'bay\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, limit, offset, sort, ids, names
# See section "Common Fields" for examples
