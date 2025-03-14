# Get all password policies
res = client.get_password_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a password policy
res = client.get_password_policies(names=['policy-name'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a password policy by id
res = client.get_password_policies(ids=['10314f42-020d-7080-8013-000ddt400013'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
