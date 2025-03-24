# Get all WORM data policy members
res = client.get_file_systems_worm_data_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by policy name
res = client.get_file_systems_worm_data_policies(
    policy_names=['test-policy-name']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by member name
res = client.get_file_systems_worm_data_policies(
    member_names=['member-name']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by policy ids
res = client.get_file_systems_worm_data_policies(
    policy_ids=['10314f42-0120d-7080-8013-000ddt400013']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by member ids
res = client.get_file_systems_worm_data_policies(
    member_ids=['10314f42-020d-7080-8013-000ddt400014']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
