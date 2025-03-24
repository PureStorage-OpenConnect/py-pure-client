# list TLS policies for members
res = client.get_tls_policies_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list TLS policies for specific member
res = client.get_tls_policies_members(member_names=["datavip1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list TLS policies for specific member by id
res = client.get_tls_policies_members(member_ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list only members belonging to a specific policy by name
res = client.get_tls_policies_members(policy_names=["strong-tls-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list only members with a specific policy by id
res = client.get_tls_policies_members(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
