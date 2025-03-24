# Get all WORM data policies
res = client.get_worm_data_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a WORM data policy
res = client.get_worm_data_policies(names=['policy-name'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a WORM data policy by id
res = client.get_worm_data_policies(ids=['10314f42-020d-7080-8013-000ddt400013'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
