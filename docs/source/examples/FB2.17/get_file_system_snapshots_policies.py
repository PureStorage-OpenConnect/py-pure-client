# list all policies
res = client.get_file_system_snapshots_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# assume we have a policy named "p1", and a file system snapshot named "myfs.1"
res = client.get_file_system_snapshots_policies(policy_names=["p1"],
                                                member_names=["myfs.1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list and sort by name in descendant order
res = client.get_file_system_snapshots_policies(limit=5, sort="policy.name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, member_ids, policy_ids, offset
# See section "Common Fields" for examples
