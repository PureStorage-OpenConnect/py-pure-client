# list all policies
res = client.get_file_systems_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# assume we have a policy named "p1", and a file system named "myfs"
res = client.get_file_systems_policies(policy_names=["p1"],
                                       member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list and sort by name in descendant order
res = client.get_file_systems_policies(limit=5, sort="policy.name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with page size 5
res = client.get_file_systems_policies(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining policies
res = client.get_file_systems_policies(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, member_ids, offset, policy_ids
# See section "Common Fields" for examples
