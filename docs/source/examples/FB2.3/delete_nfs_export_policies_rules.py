# delete a policy rule by name
client.delete_nfs_export_policies_rules(names=['export_policy_1.1'])

# delete a policy rule by name with a version specifier.
# The delete will fail if the policy version differs from specified version.
# The policy_version can be retrieved from the response from
# get_nfs_export_policies, patch_nfs_export_policies, post_nfs_export_policies,
# get_nfs_export_policies_rule, patch_nfs_export_policies_rule, or post_nfs_export_policies_rule.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
client.delete_nfs_export_policies_rules(names=['export_policy_1.1'], versions=[policy_version])

# delete a policy by ID
client.delete_nfs_export_policies_rules(ids=['2a37c647-19e9-4308-b469-89d9a9753160'])
