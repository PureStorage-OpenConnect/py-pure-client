# delete a policy by name
client.delete_nfs_export_policies(names=["export_policy_1"])

# delete a policy by name with a version specifier.
# The delete will fail if the policy version differs from specified version.
# The version can be retrieved from the response from
# get_nfs_export_policies, patch_nfs_export_policies or post_nfs_export_policies.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
client.delete_nfs_export_policies(names=["export_policy_1"], versions=[policy_version])

# delete a policy by ID
client.delete_nfs_export_policies(ids=["10314f42-020d-7080-8013-000ddt400012"])
