# attach policy to a file system
# assume we have a policy named "p1", and a file system named "myfs"
client.delete_policies_file_systems(policy_names=["p1"],
                                    member_names=["myfs"])

# Other valid fields: policy_ids, member_ids
# See section "Common Fields" for examples
