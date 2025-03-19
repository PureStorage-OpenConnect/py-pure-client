# detach an audit policy from a file system
# assume we have a policy named "p1", and a file system named "myfs"
client.delete_file_systems_audit_policies(policy_names=["p1"], member_names=["myfs"])

# Other valid fields: policy_ids, member_ids
# See section "Common Fields" for examples
