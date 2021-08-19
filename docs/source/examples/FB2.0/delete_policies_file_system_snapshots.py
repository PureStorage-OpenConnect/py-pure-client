# attach policy to a file system snapshot
# assume we have a policy named "p1", and a file system snapshot named "myfs.suffix"
client.delete_policies_file_system_snapshots(policy_names=["p1"],
                                             member_names=["myfs.suffix"])

# Other valid fields: policy_ids, member_ids
# See section "Common Fields" for examples
