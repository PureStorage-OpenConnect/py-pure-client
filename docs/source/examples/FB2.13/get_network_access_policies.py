# list all network access policies
res = client.get_network_access_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list network access policies specified by name
res = client.get_network_access_policies(names=['default-network-access-policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List network access policies specified by id.
res = client.get_network_access_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
