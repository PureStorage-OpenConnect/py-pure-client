# list all policies
res = client.get_policies_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# assume we have a policy named "p1", and a file system named "myfs"
res = client.get_policies_members(policy_names=["p1"],
                                  member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
res = client.get_policies_members(policy_names=["p1"],
                                  member_names=["myfs"],
                                  remote_names=["myremote"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# assume we have a policy named "p1", and a file system snapshot named "myfs.1"
res = client.get_policies_members(policy_names=["p1"],
                                  member_names=["myfs.1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list and sort by name in descendant order
res = client.get_policies_members(limit=5, sort="policy.name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with page size 5
res = client.get_policies_members(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining policies
res = client.get_policies_members(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, local_file_system_ids, local_file_system_names,
#                     member_ids, member_types, offset, policy_ids, remote_ids, remote_file_system_ids,
#                     remote_file_system_names
# See section "Common Fields" for examples
