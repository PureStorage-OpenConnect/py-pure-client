# attach policy to a file system
# assume we have a policy named "p1", and a file system named "myfs"
res = client.post_policies_file_systems(policy_names=["p1"],
                                        member_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, member_ids, policy_ids
# See section "Common Fields" for examples
