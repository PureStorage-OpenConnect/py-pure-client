# list all ssh certificiate_authority policies
res = client.get_ssh_certificate_authority_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list ssh certificate authority policies specified by name
res = client.get_ssh_certificate_authority_policies(names=['test-policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List ssh certificate authority policies specified by id.
res = client.get_ssh_certificate_authority_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
