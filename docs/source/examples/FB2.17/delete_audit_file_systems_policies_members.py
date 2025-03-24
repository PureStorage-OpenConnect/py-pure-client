# detach an audit policy from a file system
# assume we have a policy named "p1", and a file system named "myfs"
client.delete_audit_file_systems_policies_members(policy_names=["p1"], member_names=["myfs"])

# Other valid fields: context_names, policy_ids, member_ids
# See section "Common Fields" for examples
