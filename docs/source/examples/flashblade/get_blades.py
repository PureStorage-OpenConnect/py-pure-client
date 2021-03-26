# list all blades
res = client.get_blades()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of blades by name
res = client.get_blades(names=['CH1.FB1', 'CH1.FB2'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a subset of blades by id
res = client.get_blades(ids=['100abf42-0000-4000-8023-000det400090',
                             '10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all healthy blades
res = client.get_blades(filter='status=\'healthy\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, limit, offset, sort, total_only
# See section "Common Fields" for examples
