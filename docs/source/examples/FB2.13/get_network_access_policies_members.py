# list all network access policies
res = client.get_network_access_policies_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy named, and an array named "test-array"
res = client.get_network_access_policies_members(policy_names=["default-network-access-policy"],
                                                 member_names=["test-array"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list network access policies specified by name
res = client.get_network_access_policies_members(policy_names=['default-network-access-policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List network access policies specified by member id.
res = client.get_network_access_policies_members(member_ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only members with a specific policy by id
res = client.get_network_access_policies_members(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
