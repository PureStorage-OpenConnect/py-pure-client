# remove policy with id from a file system snapshot named myfs.2
client.delete_file_system_snapshots_policies(policy_ids=["10314f42-020d-7080-8013-000ddt400090"],
                                             member_names=["myfs.2"])

# Other valid fields: context_names, policy_names, member_ids
# See section "Common Fields" for examples
