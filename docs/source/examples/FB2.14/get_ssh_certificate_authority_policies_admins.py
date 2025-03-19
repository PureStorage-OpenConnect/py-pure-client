# list all ssh ca policy members for admins
res = client.get_ssh_certificate_authority_policies_admins()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy named, and an admin member named "test-admin"
res = client.get_ssh_certificate_authority_policies_admins(policy_names=["test-policy"],
                                                           member_names=["test-admin"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list ssh certificate authority policies admin members specified by name
res = client.get_ssh_certificate_authority_policies_admins(policy_names=["test-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List ssh certificate authority policies specified by member id.
res = client.get_ssh_certificate_authority_policies_admins(member_ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list only admin members with a specific policy by id
res = client.get_ssh_certificate_authority_policies_admins(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
