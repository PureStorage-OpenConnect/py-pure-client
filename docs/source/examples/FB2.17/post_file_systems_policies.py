# attach policy to a file system
# assume we have a policy named "p1", and a file system with id
# "100abf42-0000-4000-8023-000det400090"
res = client.post_file_systems_policies(policy_names=["p1"],
                                        member_ids=["100abf42-0000-4000-8023-000det400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, policy_ids, member_names
# See section "Common Fields" for examples
