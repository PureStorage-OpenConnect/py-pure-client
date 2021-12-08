from pypureclient.flashblade import NfsExportPolicy, NfsExportPolicyRule

# Disable the policy.
policy_attr = NfsExportPolicy(enabled=False)
res = client.patch_nfs_export_policies(names=['export_policy_1'], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Bulk specify new rules for the policy.
# Note: The rules must be ordered by client type grouped by
#    IP addresses, netmasks, netgroups, and asterisk (*).
bulk_rules = [NfsExportPolicyRule(client='10.20.30.40', access='root-squash', permission='rw'),
              NfsExportPolicyRule(client='192.168.0.0/28', access='root-squash', permission='ro',
                                  security=['sys']),
              NfsExportPolicyRule(client='@devgroup', access='root-squash', permission='rw',
                                  anonuid='500', anongid='500'),
              NfsExportPolicyRule(client='*', access='root-squash', permission='ro', secure=True),
              ]
policy_attr = NfsExportPolicy(rules=bulk_rules)
res = client.patch_nfs_export_policies(names=["export_policy_1"], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update the nfs export policy with id '83efe671-3265-af1e-6dd2-c9ff155c2a18'
res = client.patch_nfs_export_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'],
                                       policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
    curr_version = res_items[0].version

# update the nfs export policy using a version retrieved from a previous get, patch or post call.
# The call to patch_nfs_export_policies will fail if the version differs from the current version.
# That indicates that the export policy or one of its rules was modified since the version
# was acquired.
res = client.patch_nfs_export_policies(names=["export_policy_1"], policy=policy_attr,
                                       versions=[curr_version])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples
