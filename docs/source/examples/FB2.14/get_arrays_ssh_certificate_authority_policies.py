# list all ssh ca policy members for arrays
res = client.get_arrays_ssh_certificate_authority_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy named, and an array member named "test-array"
res = client.get_arrays_ssh_certificate_authority_policies(policy_names=["test-policy"],
                                                           member_names=["test-array"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list ssh certificate authority policies array members specified by name
res = client.get_arrays_ssh_certificate_authority_policies(policy_names=["test-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List ssh certificate authority policies member specified by member id.
res = client.get_arrays_ssh_certificate_authority_policies(member_ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only array members with a specific policy by id
res = client.get_arrays_ssh_certificate_authority_policies(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
