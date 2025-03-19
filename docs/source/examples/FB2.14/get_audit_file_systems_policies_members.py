# list all policies
res = client.get_audit_file_systems_policies_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy named "p1", and a file system named "myfs"
res = client.get_audit_file_systems_policies_members(policy_names=["p1"],
                                       member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_audit_file_systems_policies_members(limit=5, sort="policy.name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_audit_file_systems_policies_members(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining policies
res = client.get_audit_file_systems_policies_members(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, member_ids, policy_ids, offset
# See section "Common Fields" for examples
