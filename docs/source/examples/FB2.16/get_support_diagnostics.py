# Get all support diagnostics
res = client.get_support_diagnostics()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

#get by name
res = client.get_support_diagnostics(names=['3'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get by id
res = client.get_support_diagnostics(ids=['4ed534f8-e47e-cd29-25f0-841811266ba3'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples

