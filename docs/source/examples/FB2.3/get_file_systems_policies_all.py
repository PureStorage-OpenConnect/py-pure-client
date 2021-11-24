# list all policies attached to the filesystem regardless of type.
res = client.get_file_systems_policies_all()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a snapshot or nfs policy named "p1", and a file system named "myfs"
res = client.get_file_systems_policies_all(policy_names=["p1"],
                                           member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all policies attached to file system named "myfs"
res = client.get_file_systems_policies_all(member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, member_ids, offset, sort, policy_ids
# See section "Common Fields" for examples
