# list Directory Services configuration
res = client.get_directory_services_roles()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list settings configuration for a specific role
ROLE_NAME = 'array_admin'
res = client.get_directory_services_roles(role_names=[ROLE_NAME])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, ids, filter, limit, offset, role_ids, sort
# See section "Common Fields" for examples
